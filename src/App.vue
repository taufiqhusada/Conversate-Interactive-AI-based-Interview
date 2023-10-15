<template>
  <div class="container">
    <br>
    <h1>Mock Interview Annotation Tool</h1>
    <div class="row">
        <VideoUploader @transcript-updated="updateTranscript" class="col-sm-6" />
        <TranscriptDisplay :transcript="transcript" class="col-sm-6"/>
    </div>
  </div>
</template>

<script lang="ts">
import { ref } from 'vue';
import VideoUploader from '@/components/VideoUploader.vue';
import TranscriptDisplay from '@/components/TranscriptDisplay.vue';

export default {
  components: {
    VideoUploader,
    TranscriptDisplay,
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

</style>