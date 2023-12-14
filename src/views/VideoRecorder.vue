<template>
  <div>
    <video ref="videoElement" autoplay muted></video>
    <button @click="startVideo" :disabled="videoRecording">Start Video</button>
    <button @click="stopVideo" :disabled="!videoRecording">Stop Video</button>
    <button @click="startAudio" :disabled="audioRecording">Start Audio</button>
    <button @click="stopAudio" :disabled="!audioRecording">Stop Audio</button>
    <a v-if="videoRecordingFinished" :href="videoRecordingUrl" download="recorded-video.webm">Download Video</a>
    <a v-if="audioRecordingFinished" :href="audioRecordingUrl" download="recorded-audio.webm">Download Audio</a>
  </div>
</template>

<script lang="ts">
import { ref } from 'vue';
import GPTService from '@/services/gptService';

export default {
  name: 'WebcamRecorder',
  data() {
    return {
      videoRecording: false,
      audioRecording: false,
      videoRecordingFinished: false,
      audioRecordingFinished: false,
      videoRecordingUrl: '',
      audioRecordingUrl: '',
      videoMediaRecorder: null as MediaRecorder | null,
      audioMediaRecorder: null as MediaRecorder | null,
      videoStartTime: null as Date | null, // Store video start time
      audioStartTimestamps: [] as Number[],
      responseStartTimestamps: [] as Number[],
      responseAudios: [] as any[],
      backendURL: import.meta.env.VITE_BACKEND_URL,
    };
  },
  mounted() {
    this.getMedia();
  },
  methods: {
    async getMedia() {
      try {
        const videoStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });

        const videoElement = this.$refs.videoElement as HTMLVideoElement;
        videoElement.srcObject = videoStream;

        this.videoMediaRecorder = new MediaRecorder(videoStream);
        this.audioMediaRecorder = new MediaRecorder(audioStream);

        this.videoMediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.videoRecordingUrl = URL.createObjectURL(event.data);

            this.mergeVideoAndAudio(event.data);
          }
        };

        this.audioMediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {

            this.audioRecordingUrl = URL.createObjectURL(event.data);

            const gptService = new GPTService();
            // Send the audioBlob to the Whisper API to get the transcript
            gptService.getTranscriptFromWhisper(event.data).then(
              transcript => {
                console.log(transcript);

                gptService.generateGptResponse(transcript).then(async ttsResponseData => {
                  // Play the TTS audio
                  const audioContext = new AudioContext();
                                    // Convert the Blob into an ArrayBuffer
                  const arrayBuffer = await ttsResponseData.arrayBuffer();

                  // Decode the ArrayBuffer into audio data
                  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

                  const source = audioContext.createBufferSource();
                  source.buffer = audioBuffer;
                  source.connect(audioContext.destination);
                  source.start();

                  this.responseStartTimestamps.push(this.getTimeElapsed());
                  this.audioStartTimestamps.push(this.getTimeElapsed());
                  this.responseAudios.push(ttsResponseData);
                });
              }
            );
          }
        };

      } catch (err) {
        console.error('Error accessing webcam:', err);
      }
    },
    startVideo() {
      if (this.videoMediaRecorder) {
        this.videoRecordingFinished = false;
        this.videoRecording = true;
        this.videoStartTime = new Date(); // Store video start time
        this.videoMediaRecorder.start();
      }
    },
    stopVideo() {
      if (this.videoMediaRecorder && this.videoRecording) {
        this.videoMediaRecorder.stop();
        this.videoRecording = false;
        this.videoRecordingFinished = true;
      }
    },
    startAudio() {
      if (this.audioMediaRecorder) {
        this.audioRecordingFinished = false;
        this.audioRecording = true;
        this.audioMediaRecorder.start();

        this.audioStartTimestamps.push(this.getTimeElapsed());
      }
    },
    stopAudio() {
      if (this.audioMediaRecorder && this.audioRecording) {
        this.audioMediaRecorder.stop();
        this.audioRecording = false;
        this.audioRecordingFinished = true;
      }
    },
    getTimeElapsed(): number {
      if (this.videoStartTime) {
        const currentTime = new Date();
        const elapsedSeconds = (currentTime.getTime() - this.videoStartTime.getTime()) / 1000;
        return elapsedSeconds
      }
      return -1;
    },
    async mergeVideoAndAudio(videoBlob : Blob) {
      if (this.videoRecordingUrl) {
        console.log("merging")
        console.log(this.responseAudios);
        console.log(this.responseStartTimestamps);
        // Create a FormData object to send the video file
        const formData = new FormData();
        formData.append('video', videoBlob);
        for (let i = 0; i < this.responseAudios.length; i++) {
          formData.append('audio', this.responseAudios[i]);
        }
        formData.append('start_times',  JSON.stringify(this.responseStartTimestamps))

        // Define the URL of your backend endpoint for video
        const APIendpoint = `${this.backendURL}/video/merge`;

        try {
          const response = await fetch(APIendpoint, {
            method: 'POST',
            body: formData,
          });

          if (response.ok) {
            console.log('Video file merged successfully.');

            const mergedVideoBlob = await response.blob();
            console.log(mergedVideoBlob);
            this.videoRecordingUrl = URL.createObjectURL(mergedVideoBlob);

            console.log('Merged video is ready to download');
          } else {
            console.error('Failed to merge video file.');
          }
        } catch (error) {
          console.error('Error:', error);
        }
      }
    },
  },
};
</script>
