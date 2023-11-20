<template>
  <div>
    <template v-if="!videoUrl">
      <!-- Show uploader if the video has not been uploaded -->
      <form ref="fileUploadForm" class="uploader absolute-center">
        <input type="file" accept="video/*" @change="uploadFile" />

        <label for="file-upload">
          <div>
            <i class="fa fa-download" aria-hidden="true"></i>
            <div>Select a video or drag here</div>
            <div ref="notVideo" class="hidden">Please select a video</div>
            <button class="btn btn-dark" @click.prevent="selectFile">Upload a video</button>
          </div>
          <div ref="response" class="hidden">
            <div ref="messages"></div>
            <progress class="progress" ref="fileProgress" value="0" max="100">
              <span>0</span>%
            </progress>
          </div>
        </label>
      </form>
    </template>

    <video v-else controls width="640" height="360" ref="videoPlayerRef" @timeupdate="updateSeekTime">
      <source :src="videoUrl" type="video/mp4" />
    </video>
  </div>
</template>

<script lang="ts">
import { ref, defineComponent, onMounted, watch } from 'vue';
import firebase from 'firebase/app';
import 'firebase/storage';
import SymblService from '@/services/symblService';

export default defineComponent({
  props: {
    clickedTranscriptTime: {
      type: Number,
    },
  },
  setup(props, context) {
    const videoUrl = ref<string | null>(null);
    const videoPlayerRef = ref<HTMLVideoElement | null>(null);
    const fileProgress = ref<HTMLProgressElement | null>(null);
    const prevVideoSeekTime = ref<number>(0);

    const uploadTranscript = async (transcript: any[], sessionID: string) => {
      const transcriptFileName = `${sessionID}.json`;

      const storageRef = firebase.storage().ref(`transcripts/${transcriptFileName}`);
      const transcriptBlob = new Blob([JSON.stringify(transcript)], { type: 'application/json' });

      try {
        await storageRef.put(transcriptBlob);
        console.log('Transcript uploaded successfully');
      } catch (error) {
        console.error('Error uploading transcript:', error);
      }
    };

    const getTranscript = async (sessionID: string) => {
      const transcriptFileName = `${sessionID}.json`;

      const storageRef = firebase.storage().ref(`transcripts/${transcriptFileName}`);

      try {
        const downloadURL = await storageRef.getDownloadURL();
        const response = await fetch(downloadURL);
        const transcript = await response.json();

        console.log('Transcript retrieved successfully:', transcript);

        // Do something with the transcript data, e.g., pass it to a component or perform further processing.
        return transcript;
      } catch (error) {
        console.error('Error retrieving transcript:', error);
      }
    };

    const uploadFile = async (event: Event) => {
      const file = (event.target as HTMLInputElement).files?.[0];
      if (file) {
        const env = import.meta.env.VITE_ENV
        if (env == 'dev') {  // handle case in dev env, just use sample video
          let devSessionID = import.meta.env.VITE_DEV_SAMPLE_SESSION_ID
          let transcript = await getTranscript(devSessionID);
          videoUrl.value = import.meta.env.VITE_DEV_SAMPLE_VIDEO_URL

          context.emit('transcript-updated', transcript, devSessionID);
          return
        }

        const fileName = `${file.name}_${Date.now()}`;

        const storageRef = firebase.storage().ref(`videos/${fileName}`);
        const uploadTask = storageRef.put(file);

        uploadTask.on(
          'state_changed',
          (snapshot) => {
            if (fileProgress.value) {
              const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
              fileProgress.value.value = progress;
              fileProgress.value.getElementsByTagName('span')[0].innerText = Math.round(progress) + '%';
            }
          },
          (error) => {
            console.error('Error during upload:', error);
          },
          () => {
            uploadTask.snapshot.ref.getDownloadURL().then((downloadURL) => {
              // uploaded successfully but still waiting for transcript
              context.emit('video-uploaded', true)

              videoUrl.value = downloadURL;
              const appId = import.meta.env.VITE_SYMBL_APP_ID;
              const appSecret = import.meta.env.VITE_SYMBL_APP_SECRET;
              const symblService = new SymblService();

              symblService.transcribeVideo(videoUrl.value || '', appId, appSecret)
                .then(([transcript, sessionID]) => {
                  context.emit('transcript-updated', transcript, sessionID);
                  uploadTranscript(transcript, sessionID);
                })
                .catch((error) => {
                  console.error('Error transcribing video:', error);
                });
            });
          }
        );

      }
    };

    const selectFile = () => {
      const fileUpload = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileUpload) {
        fileUpload.click();
      }
    };

    const fileDragHover = (e: Event) => {
      // Handle file drag hover events
    };

    const output = (msg: string) => {
      const m = document.getElementById('messages') as HTMLElement;
      if (m) {
        m.innerHTML = msg;
      }
    };

    const setProgressMaxValue = (e: ProgressEvent) => {
      const pBar = document.getElementById('file-progress') as HTMLProgressElement;
      if (pBar && e.lengthComputable) {
        pBar.max = e.total;
      }
    };

    const updateFileProgress = (e: ProgressEvent) => {
      const pBar = document.getElementById('file-progress') as HTMLProgressElement;
      if (pBar && e.lengthComputable) {
        pBar.value = e.loaded;
      }
    };

    const updateSeekTime = () => {
      if (videoPlayerRef.value) {
        const currentTime = videoPlayerRef.value.currentTime;
        if (Math.abs(currentTime - prevVideoSeekTime.value) >= 0.1) {
          prevVideoSeekTime.value = currentTime;
          context.emit('video-seek-time-updated', currentTime);
        }
      }
    };

    const Init = () => {
      // Your Init logic remains the same
    };

    watch(() => props.clickedTranscriptTime, () => {
      if (videoPlayerRef.value && typeof props.clickedTranscriptTime === 'number') {
        videoPlayerRef.value.currentTime = props.clickedTranscriptTime;
      }
    });

    onMounted(() => {
      if (window.File && window.FileList && window.FileReader) {
        Init();
      } else {
        const fileDrag = document.getElementById('file-drag') as HTMLElement;
        if (fileDrag) {
          fileDrag.style.display = 'none';
        }
      }
    });

    return {
      videoUrl,
      uploadFile,
      selectFile,
      fileProgress,
      fileDragHover,
      output,
      setProgressMaxValue,
      updateFileProgress,
      Init,
      updateSeekTime,
      videoPlayerRef,
    };
  }
});
</script>

<style scoped>
.uploader {
  display: block;
  clear: both;
  margin: 0 auto;
  width: 100%;
  max-width: 600px;
}

.uploader label {
  float: left;
  clear: both;
  width: 100%;
  padding: 2rem 1.5rem;
  text-align: center;
  background: #fff;
  border-radius: 7px;
  border: 3px solid #eee;
  transition: all .2s ease;
  user-select: none;
}

.uploader label:hover {
  border-color: #454cad;
}

.uploader label.hover {
  border: 3px solid #454cad;
  box-shadow: inset 0 0 0 6px #eee;
}

.uploader label.hover #start i.fa {
  transform: scale(0.8);
  opacity: 0.3;
}

.uploader #start {
  float: left;
  clear: both;
  width: 100%;
}

.uploader #start.hidden {
  display: none;
}

.uploader #start i.fa {
  font-size: 50px;
  margin-bottom: 1rem;
  transition: all .2s ease-in-out;
}

.uploader #response {
  float: left;
  clear: both;
  width: 100%;
}

.uploader #response.hidden {
  display: none;
}

.uploader #response #messages {
  margin-bottom: .5rem;
}

.uploader #file-image {
  display: inline;
  margin: 0 auto .5rem auto;
  width: auto;
  height: auto;
  max-width: 180px;
}

.uploader #file-image.hidden {
  display: none;
}

.uploader #notimage {
  display: block;
  float: left;
  clear: both;
  width: 100%;
}

.uploader #notimage.hidden {
  display: none;
}

.uploader progress,
.uploader .progress {
  display: inline;
  clear: both;
  margin: 0 auto;
  width: 100%;
  max-width: 180px;
  height: 8px;
  border: 0;
  border-radius: 4px;
  background-color: #eee;
  overflow: hidden;
}

.uploader .progress[value]::-webkit-progress-bar {
  border-radius: 4px;
  background-color: #eee;
}

.uploader .progress[value]::-webkit-progress-value {
  background: linear-gradient(to right, #3f4b97 0%, #454cad 50%);
  border-radius: 4px;
}

.uploader .progress[value]::-moz-progress-bar {
  background: linear-gradient(to right, #3f4b97 0%, #454cad 50%);
  border-radius: 4px;
}

.uploader input[type="file"] {
  display: none;
}

.uploader div {
  margin: 0 0 .5rem 0;
  color: #5f6982;
}

.uploader .btn {
  display: inline-block;
  margin: .5rem .5rem 1rem .5rem;
  clear: both;
  font-family: inherit;
  font-weight: 700;
  font-size: 14px;
  text-decoration: none;
  text-transform: initial;
  border: none;
  border-radius: .2rem;
  outline: none;
  padding: 0 1rem;
  height: 36px;
  line-height: 36px;
  color: #fff;
  transition: all 0.2s ease-in-out;
  box-sizing: border-box;
  /* background: #454cad;
  border-color: #454cad; */
  cursor: pointer;
}

.absolute-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
</style>
