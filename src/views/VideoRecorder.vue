<template>
  <div class="container">
    <template v-if="!videoRecordingUrl">
      <video ref="videoElement" autoplay muted></video>
      <button @click="startVideo" :disabled="videoRecording">Start Video</button>
      <button @click="stopVideo" :disabled="!videoRecording">Stop Video</button>
      <button @click="startAudio" :disabled="audioRecording">Start Audio</button>
      <button @click="stopAudio" :disabled="!audioRecording">Stop Audio</button>
    </template>
    <template v-else>
      <div class="row">
        <div class="col-sm-6">
          <div class="video-uploader-container">
            <VideoPlayer :videoUrl="videoRecordingUrl" @video-seek-time-updated="updateCurrentVideoSeekTime"
              :clickedTranscriptTime="clickedTranscriptTime"></VideoPlayer>
          </div>
          <div class="col-sm-12 mt-3">
            <TranscriptDisplay :transcript="transcript" :timestampHighlights="timestampHighlightsData"
              :currentVideoSeekTime="currentVideoSeekTime" @transcript-clicked="handleTranscriptClick" />
          </div>
        </div>
        <div class="col-sm-6">
          <Feedback :showAnnotationTextboxes="true" :transcript="transcript"
            :sessionID="sessionID" @highlight-transcript="setHighlightTranscript" />
        </div>
      </div>
    </template>
  </div>
</template>

<script lang="ts">
import { ref } from 'vue';
import GPTService from '@/services/gptService';
import VideoPlayer from '@/components/V2/VideoPlayer.vue';
import TranscriptDisplay from '@/components/TranscriptDisplay.vue';
import Feedback from '@/components/Feedback.vue';


export default {
  name: 'WebcamRecorder',
  components: {
    VideoPlayer,
    TranscriptDisplay,
    Feedback
  },
  data() {
    return {
      videoRecording: false,
      audioRecording: false,
      videoRecordingFinished: false,
      audioRecordingFinished: false,
      videoRecordingUrl: ref<string | null>(null),
      audioRecordingUrl: '',
      videoMediaRecorder: null as MediaRecorder | null,
      audioMediaRecorder: null as MediaRecorder | null,
      videoStartTime: null as Date | null, // Store video start time
      userAudioStartTimestamps: [] as Number[],
      responseStartTimestamps: [] as Number[],
      idxUserAudio: 0,
      responseAudios: [] as any[],
      backendURL: import.meta.env.VITE_BACKEND_URL,

      transcript: ref<any[]>([]),
      sessionID: ref(""),
      timestampHighlightsData: ref<[number, number][]>([]),
      transcriptLoading: ref(false),
      currentVideoSeekTime: ref<number>(0),
      clickedTranscriptTime: ref<number>(0)
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
            this.mergeVideoAndAudio(event.data);
          }
        };

        this.audioMediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {

            this.audioRecordingUrl = URL.createObjectURL(event.data);

            const gptService = new GPTService();
            // Send the audioBlob to the Whisper API to get the transcript
            gptService.getTranscriptFromWhisper(event.data).then(
              transcriptFromUser => {
                console.log(transcriptFromUser);
                this.transcript.push({
                  text: transcriptFromUser,
                  timeOffset: this.userAudioStartTimestamps[this.idxUserAudio++],
                  speaker: 'User',
                })

                gptService.generateGptResponse(transcriptFromUser).then(async gptResponse => {
                  const ttsResponseData = gptResponse[0];
                  const gptResponseText = gptResponse[1];

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


                  const timeNow = this.getTimeElapsed()
                  this.responseStartTimestamps.push(timeNow);
                  this.responseAudios.push(ttsResponseData);

                  this.transcript.push({
                    text: gptResponseText,
                    timeOffset: timeNow,
                    speaker: 'Assistant',
                  })
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

        this.userAudioStartTimestamps.push(this.getTimeElapsed());
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
    async mergeVideoAndAudio(videoBlob: Blob) {
      console.log("merging")
      console.log(this.responseAudios);
      console.log(this.responseStartTimestamps);
      // Create a FormData object to send the video file
      const formData = new FormData();
      formData.append('video', videoBlob);
      for (let i = 0; i < this.responseAudios.length; i++) {
        formData.append('audio', this.responseAudios[i]);
      }
      formData.append('start_times', JSON.stringify(this.responseStartTimestamps))

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
    },
    setHighlightTranscript(data: [number, number]){
      this.timestampHighlightsData = [];
      this.timestampHighlightsData.push(data);
    },

    handleTranscriptClick(time: number) {

      this.clickedTranscriptTime = time

    },

    updateCurrentVideoSeekTime(seekTime: number) {
      this.currentVideoSeekTime = seekTime
    }
  },

};
</script>
