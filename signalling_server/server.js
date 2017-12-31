var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http, {rejectUnauthorized: false});
var port = process.env.PORT || 3000;


var chatSuffix = "chat-";
var callSuffix = "call-";
var friendlistSuffix = "friend-";
var numUsers = 0;
var onlineUserMap = {};

// TODO: use client id in database as socket id?
// User has to be logged in to connect to socket.io
io.on('connection', function (client) {
  
    var addedUser = false;
    var callroomId = -1;
    console.log('new connection: ' + client.id);

    // Client logged in, data includes list of friends id and user id
    // Increment Number of user count, instantiate friend's sockets
    client.on('add user', function(data) {
      if (!addedUser) {
        client.userId = data['userId'];
        log("adding user");
        ++ numUsers;
        addedUser = true;
        onlineUserMap[data['userId']] = client.id;
        log('New online user map: ' + JSON.stringify(onlineUserMap));
        // Join a room of name "friend-[id]" for broadcasting event to online friends
        client.join(user(client.userId));
        client.join(friendlist(client.userId));
        client.broadcast.to(friendlist(client.userId))
          .emit('update friend', {'id':client.userId, 'field': 'status', 'online': true});
      }
     });
    
  
    client.on('add message', function(data) {
      var roomId = data['roomId'];
      var friendId = data['friendId'];
      io.in(chatroom(roomId)).emit('add message', data['message']);
      // notify friend to update friendlist
      io.in(user(friendId))
        .emit('update friend', {'id': client.userId, 'field': 'message', 'message': data['message']});
      // notify client to update their own friendlist
      io.in(user(client.userId))
        .emit('update friend', {'id': friendId, 'field': 'message', 'message': data['message']});
      log("Message text: " + data['message']['text']);
      log("To room " + roomId);
    });
    
    // TODO: rename
    // Join chat channel
    client.on('connect room', function(data) {
      client.join(chatroom(data['chatId']));
      log("connected to chat room " + data['chatId']);
    });
  
    // Listen to friend's broadcasting channels
    client.on('subscribe friend', function(data) {
      var friend_ids = intArrayFromStr(data['friend_ids']);
      for (var i = 0; i < friend_ids.length; i++) {
        client.join(friendlist(friend_ids[i]));
      } 
      log("subscribe to friendlist" + friend_ids);
    });
  
    client.on('check friend status', function(data) {
      
      var friend_ids = intArrayFromStr(data['friend_ids']);
      var ans = {};
      for (var i = 0; i < friend_ids.length; i++) {
        var friend_id = friend_ids[i];
        if (friend_id in onlineUserMap) {
          ans[friend_id] = true;
        } else {
          ans[friend_id] = false;
        }
      }
      log("check friend status: " + JSON.stringify(ans));
      io.in(user(client.userId)).emit('check friend status', ans);
    });
      
    
    client.on('disconnect', function() {
      delete onlineUserMap[client.userId];
      numUsers -= 1;
      log("Disconnect");
      log('New online user map: ' + JSON.stringify(onlineUserMap));
      client.broadcast.to(friendlist(client.userId)).
         emit('update friend', {'id':client.userId, 'field': 'status','online': false});
    });
    
  
    client.on('call', function(data) {
      var name = data['name'];
      var friendId = data['friendId'];
      var roomId = data['roomId'];
      log("calling user " + friendId + ", name: " + name);
      client.join(callroom(roomId));
      log("joining call room " + roomId);
      callroomId = roomId;
      var socketId = getSocketId(friendId);
      if (socketId) {
        var data = {'name': name, 'roomId': roomId}
        // client.broadcast.to(socketId).emit('call', data);
        client.broadcast.to(user(friendId)).emit('call', data);
        log("Broadcasted to friend for call attempt");
      } else {
        log("The attempted call user is not online");
      }
    });
      
    client.on('answer call', function(data) {
      var roomId = data['roomId'];
      var accept = data['accept'];
      if (accept) {
        log("accepted to call to call room " + roomId);
        // Both side should be in the call room at this point
        client.join(callroom(roomId));
        callroomId = roomId;
      } else {
        log("declined a call to call room " + roomId);
      }
      client.broadcast.to(callroom(roomId)).emit('answer call', {'accept': accept});
    });
  
    client.on('sdp offer', function (data) {
        client.broadcast.to(callroom(callroomId)).emit('sdp offer', data);
        log('sent sdp offer');
        // log(JSON.stringify(data));
    });

    client.on('sdp answer', function (data) {
        client.broadcast.to(callroom(callroomId)).emit('sdp answer', data);
        log('sent sdp answer');
        // log(JSON.stringify(data));
    });
    
    client.on('ice candidate', function (data) {
        client.broadcast.to(callroom(callroomId)).emit('ice candidate', data);
        log('sent ice candidate');
        // log(JSON.stringify(data));
    });
      
    client.on('end call', function(data) {
        log("ending a call at call room " + callroomId);
        client.leave(callroom(callroomId));
        callroomId = -1;
    });
              
    function log(message) {
        console.log("[" + getTime() +"]" + "[UserId" + client.userId + "]" + message);
    }
         
});
  
function getTime() {

    var date = new Date();

    var hour = date.getHours();
    hour = (hour < 10 ? "0" : "") + hour;

    var min  = date.getMinutes();
    min = (min < 10 ? "0" : "") + min;

    var sec  = date.getSeconds();
    sec = (sec < 10 ? "0" : "") + sec;

    return hour + ":" + min + ":" + sec;

}

function user(id) {
  return 'user-' + id;
}
function callroom(id) {
  return 'call-' + id;
}
      
function chatroom(id) {
  return 'chat-' + id;
}

function friendlist(id) {
  return 'friend-' + id;
}
  
function getSocketId(userId) {
  return onlineUserMap[userId];
}

function intArrayFromStr(str) {
  if (str === "[]") {
    return [];
  } else {
    var substr = str.substring(1,str.length-1);
    return substr.split(',').map(Number);
  }
}
http.listen(port, function() {
    console.log('running on http://localhost:' + port);
});
