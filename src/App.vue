
<template>
  <TheHeader></TheHeader>
  <div class="container">
    <br>
    <div class="row">
      <div class="col-sm-6">
        <VideoUploader @transcript-updated="updateTranscript" />
        <TranscriptDisplay :transcript="transcript" :timestampHighlights="timestampHighlightsData"/>
      </div>
      <Feedback class="col-sm-6" :showAnnotationTextboxes="showAnnotationTextboxes" :transcript="transcript"
        :sessionID="sessionID" @highlight-transcript="setHighlightTranscript"  />

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

export default {
  components: {
    VideoUploader,
    TranscriptDisplay,
    TheHeader,
    TheFooter,
    Feedback,
  },
  setup() {
    const transcript = ref([]);
    const showAnnotationTextboxes = ref(false)
    const sessionID = ref("")
    const timestampHighlightsData = ref<[number, number][]>([])
    // Method to update the transcript when it is obtained
    const updateTranscript = (newTranscript: never[], passedSessionID: string) => {
      console.log("called in");
      console.log(newTranscript);
      transcript.value = newTranscript;
      console.log(transcript.value);

      showAnnotationTextboxes.value = true;
      sessionID.value = passedSessionID
    };

    const setHighlightTranscript = (data: [number, number]) => {
      timestampHighlightsData.value = [];
      timestampHighlightsData.value.push(data);
      console.log(timestampHighlightsData.value)
    };

    return {
      transcript,
      updateTranscript,
      showAnnotationTextboxes,
      sessionID,
      timestampHighlightsData,
      setHighlightTranscript
    };
  },
};
</script>