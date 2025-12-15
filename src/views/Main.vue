<template>
  <div class="container">
    <br>
    <div class="row">
      <div class="col-sm-6">
        <div class="col-sm-12 mt-3">
          <TranscriptDisplay :transcript="transcript" :timestampHighlights="timestampHighlightsData" :currentVideoSeekTime="currentVideoSeekTime"
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
import TranscriptDisplay from '@/components/TranscriptDisplay.vue';
import TheHeader from '@/components/TheHeader.vue';
import TheFooter from '@/components/TheFooter.vue';
import Feedback from '@/components/Feedback.vue';
import Loader from '@/components/loader.vue';

export default {
  name: 'Main',
  components: {
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
    const currentVideoSeekTime = ref<number>(0)
    const clickedTranscriptTime = ref<number>(0)

    const setHighlightTranscript = (data: [number, number]) => {
      timestampHighlightsData.value = [];
      timestampHighlightsData.value.push(data);
    };

    const handleTranscriptClick = (time: number) => {
      clickedTranscriptTime.value = time
    }

    return {
      transcript,
      showAnnotationTextboxes,
      sessionID,
      timestampHighlightsData,
      setHighlightTranscript,
      currentVideoSeekTime,
      handleTranscriptClick,
      clickedTranscriptTime
    };
  },
};
</script>

<style>

</style>
