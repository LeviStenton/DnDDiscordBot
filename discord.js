const Discord = require('discord.js');
const client = new Discord.Client();

// Receive audio from a voice channel
const fs = require('fs');
// Create a ReadableStream of s16le PCM audio
const audio = connection.receiver.createStream(user, { mode: 'pcm' });
audio.pipe(fs.createWriteStream('user_audio'));

client.once('ready', () => {
	console.log('Ready!');
});

if (message.content === '!ping') {
	// send back "Pong." to the channel the message was sent in
	message.channel.send('Pong.');
}

client.login('NzE1MTEwNTMyNTMyNzk3NDkw.Xs4clQ.wu4OJ5-yQbUIyiVzrzjzkmI0Rzk');