<template>
  <div class="container">
    <template v-if="!videoRecordingUrl">
      <div class="videoRecorderDiv text-center mt-5">
        <video class="webcam shadow" ref="videoElement" autoplay muted></video> <br>
        <button class="btn btn-outline-primary m-2" @click="startVideo" v-if="!videoRecording && !showLoader">Start Session</button>
        <button class="btn btn-outline-primary m-2" @click="stopVideo" v-if="videoRecording && !showLoader && !showSpeaker">Stop Session</button>
        <button class="btn btn-outline-primary m-2" @click="startAudio" v-if="!audioRecording && videoRecording && !showLoader && !showSpeaker">Start
          Audio</button>
        <button class="btn btn-outline-primary m-2" @click="stopAudio" v-if="audioRecording && !showLoader && !showSpeaker">Stop Recording</button>
        <Speaker v-if="showSpeaker"></Speaker>
        <Loader v-if="showLoader"></Loader>
      </div>
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
          <Feedback :showAnnotationTextboxes="true" :transcript="transcript" :sessionID="sessionID"
            @highlight-transcript="setHighlightTranscript" />
        </div>
      </div>
    </template>
  </div>
</template>

<script lang="ts">
import { ref, onMounted } from 'vue';
import GPTService from '@/services/gptService'; // Import your GPT service
import { postInterviewData, postInterviewTranscriptData } from '@/services/backendService'; // Import your API services
import { v4 as uuidv4 } from 'uuid';
import VideoPlayer from '@/components/V2/VideoPlayer.vue';
import TranscriptDisplay from '@/components/TranscriptDisplay.vue';
import Feedback from '@/components/Feedback.vue';
import Speaker from '@/components/V2/Speaker.vue';
import Loader from '@/components/loader.vue';

export default {
  name: 'WebcamRecorder',
  components: {
    VideoPlayer,
    TranscriptDisplay,
    Feedback,
    Speaker,
    Loader
  },
  setup() {
    const videoElement = ref<HTMLVideoElement | null>(null);
    
    const videoRecording = ref<boolean>(false);
    const audioRecording = ref<boolean>(false);
    const videoRecordingFinished = ref<boolean>(false);
    const audioRecordingFinished = ref<boolean>(false);
    const videoRecordingUrl = ref<string | null>(null);
    const videoMediaRecorder = ref<MediaRecorder | null>(null);
    const audioMediaRecorder = ref<MediaRecorder | null>(null);
    const videoStartTime = ref<Date | null>(null);
    const userAudioStartTimestamps = ref<number[]>([]);
    const responseStartTimestamps = ref<number[]>([]);
    const idxUserAudio = ref<number>(0);
    const responseAudios = ref<Blob[]>([]);
    const backendURL = import.meta.env.VITE_BACKEND_URL as string;

    const transcript = ref<any[]>([]);
    const sessionID = ref<string>('');
    const timestampHighlightsData = ref<[number, number][]>([]);
    const transcriptLoading = ref<boolean>(false);
    const currentVideoSeekTime = ref<number>(0);
    const clickedTranscriptTime = ref<number>(0);

    const listQuestions = ref<string[]>([]);
    const listSystemInstruction = ref<string[]>([]);
    const idxInstruction = ref<number>(0);
    const depthFollowUpQuestion = 2;

    const showSpeaker = ref<boolean>(false);
    const showLoader = ref<boolean>(false);

    onMounted(() => {
      initListInstruction();
      getMedia();
    });

    const initListInstruction = () => {
      listQuestions.value = [
        "Tell me about yourself?",
        "Tell me about your past related experience?",
        "What is your strength?",
        "What is your weakness?",
      ];

      const concatenatedListQuestion = listQuestions.value.join(',');

      listSystemInstruction.value = new Array(
        listQuestions.value.length + listQuestions.value.length * depthFollowUpQuestion + 1
      );
      let j = 0;
      for (let i = 0; i < listQuestions.value.length; i++) {
        if (i === 0) {
          listSystemInstruction.value[j++] =
            "You have a role as an interviewer for Behavioral Job Interview. Act naturally as an interviewer with a dynamic but still professional. Say 'Hi, nice to meet you' first, introduce yourself, your name is Mr Interviewer, then ask this first question as the first question for the interview: " +
            listQuestions.value[0];
        } else {
          listSystemInstruction.value[j++] = `As an interviewer move to the next question (but still make the interaction smooth). Ask this question to the interviewee: '${listQuestions.value[i]}'`;
        }

        for (let cnt = 0; cnt < depthFollowUpQuestion; ++cnt) {
          listSystemInstruction.value[j++] =
            `As an interviewer ask a follow-up question based on the user previous answers and based on your previous question. Your follow-up question cannot be similar to the questions on this list [${concatenatedListQuestion}] and cannot be the same as your previous questions`;
        }
      }
      listSystemInstruction.value[listSystemInstruction.value.length - 1] =
        "Now say that the interview process is over and thank you for the time";
    };

    const getMedia = async () => {
      try {
        const videoStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true  });
        const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });

        if (videoElement.value) {
          videoElement.value.srcObject = videoStream;
        }
        videoMediaRecorder.value = new MediaRecorder(videoStream);
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
            mergeVideoAndAudio(event.data);
          }
        };

        audioMediaRecorder.value.ondataavailable = (event) => {
          if (event.data.size > 0) {
            const gptService = new GPTService();
            gptService.getTranscriptFromWhisper(event.data).then((listTranscriptFromUser) => {
              console.log(listTranscriptFromUser)
              listTranscriptFromUser.forEach((item) => {
                const timeStartOffset = userAudioStartTimestamps.value[idxUserAudio.value++];
                transcript.value.push({
                  text: item.text,
                  timeOffset: item.startTime + timeStartOffset,
                  speaker: 'User',
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
          const ttsResponseData = gptResponse[0];
          const gptResponseText = gptResponse[1];

          const audioContext = new AudioContext();

          const audioData = atob(ttsResponseData);

          // Convert the audio data to an ArrayBuffer
          const audioBuffer = new ArrayBuffer(audioData.length);
          const audioView = new Uint8Array(audioBuffer);
          for (let i = 0; i < audioData.length; i++) {
            audioView[i] = audioData.charCodeAt(i);
          }

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
          });
          showSpeaker.value = true;

          const timeNow = getTimeElapsed();
          responseStartTimestamps.value.push(timeNow);
          responseAudios.value.push(ttsResponseData);

          transcript.value.push({
            text: gptResponseText,
            timeOffset: timeNow,
            speaker: 'Assistant',
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

    const mergeVideoAndAudio = async (videoBlob: Blob) => {
      showLoader.value = true;
      console.log('merging');
      // Create a FormData object to send the video file
      const formData = new FormData();
      formData.append('video', videoBlob);
      for (let i = 0; i < responseAudios.value.length; i++) {
        formData.append('audio', responseAudios.value[i]);
      }
      formData.append('start_times', JSON.stringify(responseStartTimestamps.value));

      // Define the URL of your backend endpoint for video
      const APIendpoint = `${backendURL}/video/merge`;

      try {
        const response = await fetch(APIendpoint, {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          console.log('Video file merged successfully.');
          const mergedVideoBlob = await response.blob();

          let myuuid = uuidv4();
          sessionID.value = `${myuuid}_${Date.now()}`;

          await postInterviewData({
            sessionID: sessionID.value,
            username_interviewer: 'interviewer_username',
            username_interviewee: 'interviewee_username',
            transcript_link: 'none',
            video_link: 'none',
          });

          await postInterviewTranscriptData({
            sessionID: sessionID.value,
            transcript: transcript.value,
          });

          showLoader.value = false;

          videoRecordingUrl.value = URL.createObjectURL(mergedVideoBlob);

          console.log('Merged video is ready to download');
        } else {
          console.error('Failed to merge video file.');
        }
      } catch (error) {
        console.error('Error:', error);
        alert("error" + error);
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

    return {
      videoElement,
      videoRecording,
      audioRecording,
      videoRecordingFinished,
      audioRecordingFinished,
      videoRecordingUrl,
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
      timestampHighlightsData,
      transcriptLoading,
      currentVideoSeekTime,
      clickedTranscriptTime,
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
      setHighlightTranscript,
      handleTranscriptClick,
      updateCurrentVideoSeekTime,
    };
  },
};
</script>


<style scoped>
.webcam {
  border-radius: 5%;
  max-height: 20rem;
}
</style>