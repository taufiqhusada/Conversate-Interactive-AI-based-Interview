<template>
  <div class="container">
    <div class="card text-center" style="width: 50vh;">
      <div class="card-header">
        {{ currentIndex+1 }} / {{ questions.length }} Main Questions
      </div>
      <ul class="list-group list-group-flush">
        <li class="list-group-item">{{ questions[currentIndex] }}</li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  props: {
    questions: {
      type: Array<string>,
      required: true,
    },
    currentIndex: {
      type: Number,
      required: true,
      default: 0,
    },
  }
};
</script>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
