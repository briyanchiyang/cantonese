const switcher = document.querySelector('.btn');

switcher.addEventListener('click', function() {
    document.body.classList.toggle('on');
    document.body.classList.toggle('off');

    navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {

        // Change button
        var emoji = String.fromCodePoint(0x0001F507);
        this.textContent = "Recording!  ".concat(emoji);

        // Take in audio
        //const mediaRecorder = new MediaRecorder(stream);
        //mediaRecorder.start();

        //const audioChunks = [];
        //mediaRecorder.addEventListener("dataavailable", event => {
        //    audioChunks.push(event.data);
        //});
    
        //// Stop audio
        //mediaRecorder.addEventListener("stop", () => {
        //    const audioBlob = new Blob(audioChunks);
        //    const audioUrl = URL.createObjectURL(audioBlob);
        //    const audio = new Audio(audioUrl);
        //    audio.play();
        //});

        //setTimeout(() => {
        //    mediaRecorder.stop();
        //  }, 3000);
          
    });
});


//navigator.mediaDevices.getUserMedia({ audio: true })
//  .then(stream => {
//    const mediaRecorder = new MediaRecorder(stream);
//    mediaRecorder.start();
//  });