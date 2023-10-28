<template>
  <TheHeader></TheHeader>
  <div class="container">
    <br>
    <div class="row">
      <div class="col-sm-6">
        <div class="video-uploader-container">
          <VideoUploader @transcript-updated="updateTranscript" @video-uploaded="startLoadingTranscript" />
        </div>
        <div class="col-sm-12 text-center mt-3" v-if="transcriptLoading">
          <Loader></Loader>
        </div>
        <div class="col-sm-12 mt-3">
          <TranscriptDisplay v-if="!transcriptLoading" :transcript="transcript" :timestampHighlights="timestampHighlightsData"/>
        </div>
      </div>
      <div class="col-sm-6">
        <Feedback :showAnnotationTextboxes="showAnnotationTextboxes" :transcript="transcript"
          :sessionID="sessionID" @highlight-transcript="setHighlightTranscript" />
      </div>
    </div>
  </div>
  <TheFooter></TheFooter>
</template>

<script lang="ts">
import { ref } from 'vue';
import VideoUploader from '@/components/VideoUploader.vue';
import TranscriptDisplay from '@/components/TranscriptDisplay.vue';
import TheHeader from './components/TheHeader.vue';
import TheFooter from './components/TheFooter.vue';
import Feedback from '@/components/Feedback.vue';
import Loader from '@/components/loader.vue';

export default {
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

    // Method to update the transcript when it is obtained
    const updateTranscript = (newTranscript: never[], passedSessionID: string) => {
      console.log("called in");
      console.log(newTranscript);
      transcript.value = newTranscript;
      console.log(transcript.value);

      showAnnotationTextboxes.value = true;
      sessionID.value = passedSessionID;

      // Set loading state for TranscriptDisplay to false when transcript is updated
      transcriptLoading.value = false;
    };

    const setHighlightTranscript = (data: [number, number]) => {
      timestampHighlightsData.value = [];
      timestampHighlightsData.value.push(data);
      console.log(timestampHighlightsData.value)
    };

    const startLoadingTranscript = (value: boolean) => {
      transcriptLoading.value = true
    }

    return {
      transcript,
      updateTranscript,
      showAnnotationTextboxes,
      sessionID,
      timestampHighlightsData,
      setHighlightTranscript,
      transcriptLoading,
      startLoadingTranscript
    };
  },
};
</script>

<style>

</style>
