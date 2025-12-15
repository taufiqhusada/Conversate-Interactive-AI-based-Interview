<template>
  <TheHeader></TheHeader>
  <div class="container">
      <div class="videoRecorderDiv text-center mt-5">
        <video class="webcam shadow" ref="videoElement" autoplay muted></video> <br>
        <QuestionWindow v-if="!audioRecording && videoRecording && !showLoader && !showSpeaker && ((idxInstruction-1) % (depthFollowUpQuestion+1) == 0)" class="d-flex justify-content-center mt-5" :questions="listQuestions" :currentIndex="Math.floor((idxInstruction-1)/(depthFollowUpQuestion+1))"></QuestionWindow>
       
        <input v-if="!videoRecording && !showLoader" type="text" class="form-control input-job text-center mt-4" v-model="inputJob" placeholder="Input the Job Title You Want to Apply for">
        <button class="btn btn-outline-primary mt-4" @click="startVideo" v-if="!videoRecording && !showLoader">Start Interview Session</button>
       
        <button class="click-to-talk-button mt-4" @click="startAudio" v-if="!audioRecording && videoRecording && !showLoader && !showSpeaker && (idxInstruction < listSystemInstruction.length)">
          <img src="/images/mic.png" alt="Microphone Icon" class="microphone-icon" />
          Click to Talk
        </button>
        <button class="button-recording mt-4" @click="stopAudio" v-if="audioRecording && !showLoader && !showSpeaker">Recording</button>
       
        <br>
        <button class="btn btn-outline-danger mt-4" @click="stopVideo" v-if="videoRecording && !showLoader && !showSpeaker && !audioRecording">Stop Session</button>
        <Speaker v-if="showSpeaker"></Speaker>
        <Loader v-if="showLoader"></Loader>
      </div>
  </div>
</template>
<script lang="ts">
import { ref, onMounted } from 'vue';
import GPTService from '@/services/gptService'; // Import your GPT service
import { postInterviewData, postInterviewTranscriptData } from '@/services/backendService'; // Import your API services
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import QuestionWindow from '@/components/V2/questionWindow.vue';
import Cookies from 'js-cookie';
import router from '@/router';
import Speaker from '@/components/V2/Speaker.vue';
import Loader from '@/components/loader.vue';
import TheHeader from '@/components/TheHeader.vue';

interface IdentifiedMoment {
  quality: string;
  timeOffset_start: number;
  timeOffset_end: number;
}

export default {
  name: 'WebcamRecorder',
  components: {
    QuestionWindow,
    Speaker,
    Loader,
    TheHeader,
  },
  setup() {
    const videoElement = ref<HTMLVideoElement | null>(null);
    const videoRecording = ref<boolean>(false);
    const audioRecording = ref<boolean>(false);
    const videoRecordingFinished = ref<boolean>(false);
    const audioRecordingFinished = ref<boolean>(false);
    const audioRecordingUrl = ref<string | null>(null);
    const videoMediaRecorder = ref<MediaRecorder | null>(null);
    const audioMediaRecorder = ref<MediaRecorder | null>(null);
    const videoStartTime = ref<Date | null>(null);
    const userAudioStartTimestamps = ref<number[]>([]);
    const responseStartTimestamps = ref<number[]>([]);
    const idxUserAudio = ref<number>(0);
    const responseAudios = ref<Blob[]>([]);
    const backendURL = '/api';
    const transcript = ref<any[]>([]);
    const sessionID = ref<string>('');
    const listQuestions = ref<string[]>([]);
    const listSystemInstruction = ref<string[]>([]);
    const idxInstruction = ref<number>(0);
    const depthFollowUpQuestion = 1;
    const showSpeaker = ref<boolean>(false);
    const showLoader = ref<boolean>(false);
    const videoStream = ref<MediaStream | null>(null);
    const pinnedStart = ref<number>();
    const pinnedEnd = ref<number>();
    const inputJob = ref<string>("");
    const identifiedMoments = ref<IdentifiedMoment[]>([])

    onMounted(() => {
      getMedia();
    });

    const initListInstruction = () => {
      listQuestions.value = [
        "Tell me about yourself?",
        "How has your previous education and experience prepared you for this job?",
        "What do you consider to be your greatest strength and why?",
        "What do you consider to be your greatest challenge (weakness)? How are you going about improving up on it?",
        
      ];
      // 5. "Describe a time when you used teamwork to achieve a goal. What was your role and the resulting outcome?"

      const concatenatedListQuestion = listQuestions.value.join(',');

      listSystemInstruction.value = new Array(
        listQuestions.value.length + listQuestions.value.length * depthFollowUpQuestion + 1
      );
      let j = 0;
      for (let i = 0; i < listQuestions.value.length; i++) {
        if (i === 0) {
          listSystemInstruction.value[j++] =
            `You have a role as an interviewer for Behavioral Job Interview for job position '${inputJob.value}'. Act naturally as an interviewer with a dynamic but still professional. Say 'Hi, nice to meet you' first, introduce yourself as the Hiring Manager, then ask this first question as the first question for the interview: ${listQuestions.value[0]}`;
        } else {
          listSystemInstruction.value[j++] = `As an interviewer move to the next question (but still make the interaction smooth). Ask this question to the interviewee: '${listQuestions.value[i]}'`;
        }

        for (let cnt = 0; cnt < depthFollowUpQuestion; ++cnt) {
          listSystemInstruction.value[j++] =
            `As an interviewer ask a relevant follow-up question to the job based on the user previous answers and based on your previous question. Your follow-up question CANNOT BE SIMILAR TO THE QUESTIONS ON THIS LIST [${concatenatedListQuestion}] and cannot be the same as your previous questions`;
        }
      }
      listSystemInstruction.value[listSystemInstruction.value.length - 1] =
        "Now say that the interview process is over and thank you for the time";

      console.log(listSystemInstruction)
    };

    const getMedia = async () => {
      try {
        videoStream.value = await navigator.mediaDevices.getUserMedia({ video: true, audio: true  });
        const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });

        const audioOnlyStream = new MediaStream();
          videoStream.value.getAudioTracks().forEach((audioTrack) => {
            audioOnlyStream.addTrack(audioTrack);
        });


        if (videoElement.value) {
          videoElement.value.srcObject = videoStream.value;
        }
        videoMediaRecorder.value = new MediaRecorder(audioOnlyStream);
        audioMediaRecorder.value = new MediaRecorder(audioStream);

        videoMediaRecorder.value.onstart = async () => {
          showLoader.value = true;
          videoRecordingFinished.value = false;
          videoRecording.value = true;
          videoStartTime.value = new Date(); // Store video start time
          
          generateAssistantResponse();
          
        };

        videoMediaRecorder.value.ondataavailable = (event) => {
          if (event.data.size > 0) {
            mergeAudioFiles(event.data);
          }
        };

        audioMediaRecorder.value.ondataavailable = (event) => {
          if (event.data.size > 0) {
            const gptService = new GPTService();
            gptService.getTranscriptFromWhisper(event.data).then((listTranscriptFromUser) => {
              console.log(listTranscriptFromUser)
              const timeStartOffset = userAudioStartTimestamps.value[idxUserAudio.value++];

              listTranscriptFromUser.forEach((item) => {
                transcript.value.push({
                  text: item.text,
                  timeOffset: item.startTime + timeStartOffset,
                  speaker: 'user',
                });
              });

              generateAssistantResponse();
            }).catch(error => {
              console.log("error", error);
              showSpeaker.value = false;
              showLoader.value = false;
              alert("error" + error);
            });
          }
        };
      } catch (err) {
        alert('Error accessing webcam:' + err);
        console.error('Error accessing webcam:', err);
      }
    };

    const generateAssistantResponse = () => {
      showLoader.value = true;
      const gptService = new GPTService();
      gptService.generateGptResponse(transcript.value, listSystemInstruction.value[idxInstruction.value++]).then(
        async (gptResponse) => {
          const ttsResponseData = gptResponse['audio_data'];
          const gptResponseText = gptResponse['text_response'];
          const identification = gptResponse['identification'];

          const audioContext = new AudioContext();

          const audioData = atob(ttsResponseData);

          // Convert the audio data to an ArrayBuffer
          const audioBuffer = new ArrayBuffer(audioData.length);
          const audioView = new Uint8Array(audioBuffer);
          for (let i = 0; i < audioData.length; i++) {
            audioView[i] = audioData.charCodeAt(i);
          }

          const audioBlob = new Blob([audioView], { type: 'audio/mp3' });

          // Decode the ArrayBuffer into audio data
          audioContext.decodeAudioData(audioBuffer, (decodedBuffer) => {
            const source = audioContext.createBufferSource();
            source.buffer = decodedBuffer;
            source.connect(audioContext.destination);

            source.onended = () => {
              // Audio has ended, add your logic here
              showSpeaker.value = false;
            };

            showLoader.value = false;
            source.start();
            showSpeaker.value = true;

            const timeNow = getTimeElapsed();
            responseStartTimestamps.value.push(timeNow);
            responseAudios.value.push(audioBlob);

            transcript.value.push({
              text: gptResponseText,
              timeOffset: timeNow,
              speaker: 'assistant',
            });

            if (identification['quality']=='need improvement'){
              identification['timeOffset_end'] = timeNow - 0.1;
              identifiedMoments.value.push(identification);
              console.log(identifiedMoments.value)
            }
          });
          
        }
      ).catch(error => {
        console.log("error", error);
        showSpeaker.value = false;
        showLoader.value = false;
        alert("error" + error);
      });
    };

    const startVideo = () => {
      if (videoMediaRecorder.value) {
        initListInstruction();
        videoMediaRecorder.value.start();
      }
    };

    const stopVideo = () => {
      if (videoMediaRecorder.value && videoRecording.value) {
        showLoader.value = true;
        videoMediaRecorder.value.stop();
        videoRecording.value = false;
        videoRecordingFinished.value = true;

        // Get the video tracks from the stream and stop them
        const videoTracks = videoMediaRecorder.value.stream?.getVideoTracks();
        if (videoTracks) {
          videoTracks.forEach((track) => track.stop());
        }

        if (audioMediaRecorder.value) {
          const audioTracks = audioMediaRecorder.value.stream?.getAudioTracks();
          if (audioTracks) {
            audioTracks.forEach((track) => track.stop());
          }
        }

        if (videoStream.value) {
          const tracks = videoStream.value.getTracks();
          tracks.forEach((track) => track.stop());
          videoStream.value = null;
        }
      }
    };

    const startAudio = () => {
      if (audioMediaRecorder.value) {
        audioRecordingFinished.value = false;
        audioRecording.value = true;
        audioMediaRecorder.value.start();

        userAudioStartTimestamps.value.push(getTimeElapsed());
      }
    };

    const stopAudio = () => {
      if (audioMediaRecorder.value && audioRecording.value) {
        showLoader.value = true;
        audioMediaRecorder.value.stop();
        audioRecording.value = false;
        audioRecordingFinished.value = true;
      }
    };

    const getTimeElapsed = () => {
      if (videoStartTime.value) {
        const currentTime = new Date();
        const elapsedSeconds = (currentTime.getTime() - videoStartTime.value.getTime()) / 1000;
        return elapsedSeconds;
      }
      return -1;
    };

    const mergeAudioFiles = async (userAudioBlob: Blob) => {
      showLoader.value = true;
      console.log('merging audio files');
      // Create a FormData object to send the video file
      const formData = new FormData();
      formData.append('user_audio', userAudioBlob);
      for (let i = 0; i < responseAudios.value.length; i++) {
        formData.append('audio', responseAudios.value[i]);
      }
      formData.append('start_times', JSON.stringify(responseStartTimestamps.value));

      // Define the URL of your backend endpoint for audio merging
      const APIendpoint = `${backendURL}/audio/merge`;

      try {
        const response =  await axios.post(APIendpoint, formData);

        if (response.status >= 200) {
          console.log('Audio files merged successfully.');
          const mergedAudioUrl = response.data['data']['url'];
          
          // Prepend backend URL if the URL is relative
          const fullMergedAudioUrl = mergedAudioUrl.startsWith('http') 
            ? mergedAudioUrl 
            : `${import.meta.env.VITE_BACKEND_URL}${mergedAudioUrl}`;

          let myuuid = uuidv4();
          sessionID.value = `${myuuid}_${Date.now()}`;

          const respPayload = await postInterviewData({
            sessionID: sessionID.value,
            username_interviewer: 'interviewer_username',
            username_interviewee: 'interviewee_username',
            transcript_link: 'none',
            video_link: fullMergedAudioUrl,
          });


          await postInterviewTranscriptData({
            sessionID: sessionID.value,
            transcript: transcript.value,
            identifiedMoments: identifiedMoments.value,
          });

          showLoader.value = false;

          audioRecordingUrl.value = fullMergedAudioUrl;

          // Store data in localStorage as fallback for when MongoDB is not available
          localStorage.setItem('interviewData', JSON.stringify({
            sessionID: sessionID.value,
            audioUrl: fullMergedAudioUrl,
            transcript: transcript.value,
            identifiedMoments: identifiedMoments.value,
            timestamp: Date.now()
          }));

          if ( respPayload && sessionID.value){
            Cookies.set('keto', respPayload.data.token, { expires: 120 / (24 * 60) });
            Cookies.set('sessionID', sessionID.value,  { expires: 120 / (24 * 60) });
            router.push('/reflection');
          }
         

          console.log('Merged audio is ready to play');
        } else {
          console.error('Failed to merge audio files.');
        }
      } catch (error) {
        console.error('Error:', error);
        alert("error" + error);
      }
    };

    return {
      videoElement,
      videoRecording,
      audioRecording,
      videoRecordingFinished,
      audioRecordingFinished,
      audioRecordingUrl,
      videoMediaRecorder,
      audioMediaRecorder,
      videoStartTime,
      userAudioStartTimestamps,
      responseStartTimestamps,
      idxUserAudio,
      responseAudios,
      backendURL,
      transcript,
      sessionID,
      listQuestions,
      listSystemInstruction,
      idxInstruction,
      depthFollowUpQuestion,
      showSpeaker,
      showLoader,
      startVideo,
      stopVideo,
      startAudio,
      stopAudio,
      getTimeElapsed,
      inputJob,
    };
  },
};
</script>


<style scoped>
.webcam {
  border-radius: 5%;
  max-height: 35vh;
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