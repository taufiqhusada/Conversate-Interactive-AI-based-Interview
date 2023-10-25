
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
    // Method to update the transcript when it is obtained
    const updateTranscript = (newTranscript: never[]) => {
      console.log("called in");
      console.log(newTranscript);
      transcript.value = newTranscript;
    };
    
    return {
      transcript,
      updateTranscript,
    };
  },
};
</script>

<style scoped>
.row {
  display: inline-block;
  width: 50%;
  height: auto;
  overflow-y: auto;
}

.column {
  display: inline-block;
  width: 50%;
  height: auto;
  overflow-y: auto;
}


</style>
<template>
  <the-header></the-header>
  <div class="container">
  <br>
  <h1 style="background-color: rgba(0, 0, 0, 0.496);">Mock Interview Annotation Tool</h1>
  <div class="row">
      <VideoUploader @transcript-updated="{ updateTranscript }" class="col-sm-6" />
      <TranscriptDisplay :transcript="{ transcript }" class="col-sm-6"/>
  </div>
  <div class="column">
    <Feedback :initial-settings="{ updateSettings }" class="col-sm-6"/>
  </div>
</div>
 <TheFooter></TheFooter>
</template>