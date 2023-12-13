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
      audioChunks: [] as Blob[],
      audioSegments: [] as Blob[],
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
          }
        };
        
        this.audioMediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.audioChunks.push(event.data);
          }
        };
        
        this.audioMediaRecorder.onstop = () => {
          const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
          this.audioSegments.push(audioBlob);
          this.audioRecordingUrl = URL.createObjectURL(audioBlob);
          this.audioRecordingFinished = true;
        };
        
      } catch (err) {
        console.error('Error accessing webcam:', err);
      }
    },
    startVideo() {
      if (this.videoMediaRecorder){
        this.videoRecordingFinished = false;
        this.videoRecording = true;
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
      if (this.audioMediaRecorder){
        this.audioChunks = [];
        this.audioRecordingFinished = false;
        this.audioRecording = true;
        this.audioMediaRecorder.start();
      }
    },
    stopAudio() {
      if (this.audioMediaRecorder && this.audioRecording) {
        this.audioMediaRecorder.stop();
        this.audioRecording = false;
      }
    },
  },
};
</script>
