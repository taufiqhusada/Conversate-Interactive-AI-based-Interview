<template>
  <div class="container">
    <br>
    <div class="row">
      <div class="col-sm-6">
        <div class="video-uploader-container">
          <VideoUploader @transcript-updated="updateTranscript" @video-uploaded="startLoadingTranscript" @video-seek-time-updated="updateCurrentVideoSeekTime" :clickedTranscriptTime="clickedTranscriptTime" />
        </div>
        <div class="col-sm-12 text-center mt-3" v-if="transcriptLoading">
          <Loader></Loader>
        </div>
        <div class="col-sm-12 mt-3">
          <TranscriptDisplay v-if="!transcriptLoading" :transcript="transcript" :timestampHighlights="timestampHighlightsData" :currentVideoSeekTime="currentVideoSeekTime"
          @transcript-clicked="handleTranscriptClick" :isShowingMoments="false"/>
        </div>
      </div>
      <div class="col-sm-6">
        <Feedback :showAnnotationTextboxes="showAnnotationTextboxes" :transcript="transcript"
          :sessionID="sessionID" @highlight-transcript="setHighlightTranscript" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { ref } from 'vue';
import VideoUploader from '@/components/VideoUploader.vue';
import TranscriptDisplay from '@/components/TranscriptDisplay.vue';
import TheHeader from '@/components/TheHeader.vue';
import TheFooter from '@/components/TheFooter.vue';
import Feedback from '@/components/Feedback.vue';
import Loader from '@/components/loader.vue';

export default {
  name: 'Main',
  components: {
    VideoUploader,
    TranscriptDisplay,
    TheHeader,
    TheFooter,
    Feedback,
    Loader
  },
  setup() {
    const transcript = ref([]);
    const showAnnotationTextboxes = ref(false)
    const sessionID = ref("")
    const timestampHighlightsData = ref<[number, number][]>([])
    const transcriptLoading = ref(false);
    const currentVideoSeekTime = ref<number>(0)
    const clickedTranscriptTime = ref<number>(0)

    // Method to update the transcript when it is obtained
    const updateTranscript = (newTranscript: never[], passedSessionID: string) => {
      transcript.value = newTranscript;

      showAnnotationTextboxes.value = true;
      sessionID.value = passedSessionID;

      // Set loading state for TranscriptDisplay to false when transcript is updated
      transcriptLoading.value = false;
    };

    const setHighlightTranscript = (data: [number, number]) => {
      timestampHighlightsData.value = [];
      timestampHighlightsData.value.push(data);
    };

    const startLoadingTranscript = (value: boolean) => {
      transcriptLoading.value = true
    }

    const updateCurrentVideoSeekTime = (seekTime: number) => {
      currentVideoSeekTime.value = seekTime
    }

    const handleTranscriptClick = (time: number) => {
      clickedTranscriptTime.value = time
    }

    return {
      transcript,
      updateTranscript,
      showAnnotationTextboxes,
      sessionID,
      timestampHighlightsData,
      setHighlightTranscript,
      transcriptLoading,
      startLoadingTranscript,
      updateCurrentVideoSeekTime,
      currentVideoSeekTime,
      handleTranscriptClick,
      clickedTranscriptTime
    };
  },
};
</script>

<style>

</style>
