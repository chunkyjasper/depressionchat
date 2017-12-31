var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http, {rejectUnauthorized: false});
var port = process.env.PORT || 3000;

// Super simple server:
//  * One room only. 
//  * We expect two people max. 
//  * No error handling.
app.get('/', function(req, res){
  res.sendFile(__dirname + '/index.html');
});

io.on('connection', function (client) {
    console.log('new connection: ' + client.id);

    client.on('offer', function (details) {
        client.broadcast.emit('offer', details);
        console.log('offer: ' + JSON.stringify(details));
    });

    client.on('answer', function (details) {
        client.broadcast.emit('answer', details);
        console.log('answer: ' + JSON.stringify(details));
    });
    
    client.on('candidate', function (details) {
        client.broadcast.emit('candidate', details);
        console.log('candidate: ' + JSON.stringify(details));
    });

    // Here starts evertyhing!
    // The first connection doesn't send anything (no other clients)
    // Second connection emits the message to start the SDP negotation
    client.broadcast.emit('createoffer', {});
});

http.listen(port, function() {
    console.log('running on http://localhost:' + port);
});
