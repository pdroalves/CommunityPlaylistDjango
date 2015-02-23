//Load player api asynchronously.
var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

var player;
var SCRIPT_ROOT = "/channels/"+CHANNEL_ID;
//var default_start_video = 'dQw4w9WgXcQ'
//var default_next_video = 'F0BfcdPKw8E'
var song_playing = ''
var current_time = 0
var maxDelay = 1.0


function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
      height: '100%',
      width: '100%',
      //videoId: default_start_video,      
      events: {
        'onReady': onPlayerReady
      }
    });
    ;
}

function onPlayerReady(evt) {
    console.log('playing '+song_playing)
    evt.target.playVideo();
};

var update_status_function = function(){
    $.getJSON(SCRIPT_ROOT+'/update',
        {"mode":"player"},
        function(data){
          status = data.now_playing;
          console.log(status);
          // Asserts that the video playing is the right one
            if(song_playing != status.song_id){
                console.log(status.song_id)
                player.loadVideoById(status.song_id);
                player.seekTo(status.current_time);
                song_playing = status.song_id;
            }
            // Asserts that the video position is correct
            if(player.getPlayerState() == YT.PlayerState.PLAYING || 
                player.getPlayerState() == YT.PlayerState.PAUSED){
                var diff = Math.abs(player.getCurrentTime() - status.current_time);
                if(diff > maxDelay){
                    player.seekTo(status.current_time);
                }
            }

            // Asserts that the video status is correct
            if(status.now_playing == YT.PlayerState.PLAYING){
               player.playVideo();
               console.log("Play");
            }else if(status.now_playing == YT.PlayerState.PAUSED){
               player.pauseVideo();
               console.log("Pause");
            }else{
               player.stopVideo();
               console.log("End");
            }
        });
    };

function periodicGetStatusUpdate(){
    update_status_function();
    setTimeout(periodicGetStatusUpdate,100);
}

$(document).ready(function(){
  periodicGetStatusUpdate();
});