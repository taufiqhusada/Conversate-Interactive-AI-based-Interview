<template>
  <div>
    <video ref="videoElement" autoplay></video>
    <button @click="startRecording" :disabled="recording">Start Recording</button>
    <button @click="stopRecording" :disabled="!recording">Stop Recording</button>
    <a v-if="recordingFinished" :href="recordingUrl" download="recorded-video.webm">Download Recording</a>
  </div>
</template>

<script lang="ts">
import { ref } from 'vue';

export default {
  name: 'WebcamRecorder',
  data() {
    return {
      recording: false,
      recordingFinished: false,
      recordingUrl: '',
      mediaRecorder: null as MediaRecorder | null,
      chunks: [] as Blob[],
    };
  },
  mounted() {
    this.getMedia();
  },
  methods: {
    async getMedia() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        const videoElement = this.$refs.videoElement as HTMLVideoElement;
        videoElement.srcObject = stream;
      } catch (err) {
        console.error('Error accessing webcam:', err);
      }
    },
    startRecording() {
      const videoElement = this.$refs.videoElement as HTMLVideoElement;
      const stream = videoElement.srcObject as MediaStream;
      this.chunks = [];
      this.recording = true;
      this.mediaRecorder = new MediaRecorder(stream);
      
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.chunks.push(event.data);
        }
      };
      
      this.mediaRecorder.onstop = () => {
        const blob = new Blob(this.chunks, { type: 'video/webm' });
        this.recordingUrl = URL.createObjectURL(blob);
        this.recordingFinished = true;
      };
      
      this.mediaRecorder.start();
    },
    stopRecording() {
      if (this.mediaRecorder && this.recording) {
        this.mediaRecorder.stop();
        this.recording = false;
      }
    },
  },
};
</script>