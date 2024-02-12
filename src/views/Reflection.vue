<template>
  <div class="container">
      <div v-if="audioRecordingUrl" class="video-uploader-container">
            <VideoPlayer :audioUrl="audioRecordingUrl" @video-seek-time-updated="updateCurrentVideoSeekTime"
              :clickedTranscriptTime="clickedTranscriptTime" :identifiedMoments="identifiedMoments" :pinnedStart="pinnedStart" :pinnedEnd="pinnedEnd" :pinnedMoments="pinnedMoments"></VideoPlayer>
      </div>
      <div class="row">
        <div class="col-sm-4">
          <div class="col-sm-12 mt-3">
            <TranscriptDisplay :transcript="transcript" :timestampHighlights="timestampHighlightsData"
              :currentVideoSeekTime="currentVideoSeekTime" @transcript-clicked="handleTranscriptClick" :identifiedMoments="identifiedMoments"/>
          </div>
        </div>
        <div class="col-sm-8">
          <Feedback :showAnnotationTextboxes="true" :transcript="transcript" :sessionID="sessionID"
            @highlight-transcript="setHighlightTranscript" :currentVideoSeekTime="currentVideoSeekTime" @pin-moment="setPinMoment" @save-data="handleSaveData"/>
        </div>
      </div>
  </div>
</template>

<script lang="ts">
import { ref, onMounted } from 'vue';
import GPTService from '@/services/gptService'; // Import your GPT service
import { getAllData } from '@/services/backendService'; // Import your API services
import { v4 as uuidv4 } from 'uuid';
import VideoPlayer from '@/components/V2/VideoPlayer.vue';
import TranscriptDisplay from '@/components/TranscriptDisplay.vue';
import Feedback from '@/components/Feedback.vue';
import Speaker from '@/components/V2/Speaker.vue';
import Loader from '@/components/loader.vue';
import axios from 'axios';
import QuestionWindow from '@/components/V2/questionWindow.vue'
import Cookies from 'js-cookie'


interface IdentifiedMoment {
  quality: string;
  timeOffset_start: number;
  timeOffset_end: number;
}


export default {
  name: 'WebcamRecorder',
  components: {
    VideoPlayer,
    TranscriptDisplay,
    Feedback,
    Speaker,
    Loader,
    QuestionWindow
  },
  setup() {
    const audioRecordingUrl = ref<string | null>(null);
   
    const backendURL = '/api';

    const transcript = ref<any[]>([]);
    const sessionID = ref<string | any>('');
    const timestampHighlightsData = ref<[number, number][]>([]);
    const transcriptLoading = ref<boolean>(false);
    const currentVideoSeekTime = ref<number>(0);
    const clickedTranscriptTime = ref<number>(0);

    const identifiedMoments = ref<IdentifiedMoment[]>([])

    const pinnedStart = ref<number>();
    const pinnedEnd = ref<number>();
    const pinnedMoments =  ref<[number, number][]>([]);

    const inputJob = ref<string>("");


    onMounted(() => {
      fetchAudioRecordingAndTranscript();
    });

    const fetchAudioRecordingAndTranscript = async () => {
      try {
        // Call the backend API to get audioRecording and transcript
        sessionID.value = Cookies.get("sessionID");
        const token = Cookies.get('keto')
        if (token){
          const retrievedData = await getAllData(token);

          if (retrievedData){
            // Update the reactive variables with the fetched data
            audioRecordingUrl.value = retrievedData.interview.video_link;
            transcript.value = retrievedData.transcript;
            identifiedMoments.value = retrievedData.identifiedMoments;

            console.log("audioRecordingUrl", audioRecordingUrl.value)
          }
        }
        
        
      } catch (error) {
        console.error('Error fetching audioRecording and transcript:', error);
        // Handle error, show error message, etc.
      }
    };

  
    const setHighlightTranscript = (data: [number, number]) => {
      timestampHighlightsData.value = [];
      timestampHighlightsData.value.push(data);
    };

    const handleTranscriptClick = (time: number) => {
      clickedTranscriptTime.value = time;
    };

    const updateCurrentVideoSeekTime = (seekTime: number) => {
      currentVideoSeekTime.value = seekTime;
    };

    const setPinMoment = (isStart: boolean, time: number) => {
      if (isStart){
        pinnedStart.value = time

        if (pinnedEnd.value){
          if (pinnedStart.value > pinnedEnd.value){
            pinnedEnd.value = undefined
          }
        }

      } else {
        pinnedEnd.value = time
      }
    }

    const handleSaveData = (currentIndex: number) => {
      if (pinnedStart.value && pinnedEnd.value){
        if (currentIndex >= 0 && currentIndex < pinnedMoments.value.length) {
          pinnedMoments.value[currentIndex] = [pinnedStart.value, pinnedEnd.value]
        }
        else {
          pinnedMoments.value.push([pinnedStart.value, pinnedEnd.value])
        }
      }
    }

    return {
      backendURL,
      transcript,
      sessionID,
      timestampHighlightsData,
      transcriptLoading,
      currentVideoSeekTime,
      clickedTranscriptTime,
      setHighlightTranscript,
      handleTranscriptClick,
      updateCurrentVideoSeekTime,
      identifiedMoments,
      setPinMoment,
      pinnedStart,
      pinnedEnd,
      pinnedMoments,
      handleSaveData,
      inputJob,
      audioRecordingUrl,
    };
  },
};
</script>


<style scoped>
.webcam {
  border-radius: 5%;
  max-height: 15rem;
}

.click-to-talk-button {
  /* display: flex; */
  align-items: center;
  justify-content: center;
  padding: 10px 20px;
  background-color: white; /* Match this color to the color from your screenshot */
  border: 10px black;
  border-radius: 25px; /* This creates a rounded button, adjust as needed */
  font-size: 16px;
  color: rgb(0, 0, 136); /* Match this color to the color from your screenshot */
  cursor: pointer;
  outline: black;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* Adjust shadow to match screenshot */
  transition: background-color 0.3s;
}

.click-to-talk-button img {
  margin-right: 10px;
}

.click-to-talk-button:hover {
  background-color: #dfe7f9; /* Slightly darker color on hover */
}

.microphone-icon {
  /* Adjust the width and height to make the microphone icon smaller */
  width: 18px; /* Smaller width */
  height: 18px; /* Smaller height */
  margin-right: 8px;
}

.button-recording {
	width: 35px;
	height: 35px;
	font-size: 0;
	background-color: red;
	border: 0;
	border-radius: 35px;
	margin: 18px;
	outline: none;

  animation-name: pulse;
	animation-duration: 1.5s;
	animation-iteration-count: infinite;
	animation-timing-function: linear;
}

@keyframes pulse{
	0%{
		box-shadow: 0px 0px 5px 0px rgba(173,0,0,.3);
	}
	65%{
		box-shadow: 0px 0px 5px 13px rgba(173,0,0,.3);
	}
	90%{
		box-shadow: 0px 0px 5px 13px rgba(173,0,0,0);
	}
}

.input-job{
  max-width: 40vh;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto;
}
</style>