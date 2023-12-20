<template>
    <div id="bars" class="m-4">
      <div class="bar" v-for="(duration, index) in animationDurations" :key="index" :style="barStyle(index)"></div>
    </div>
  </template>
  
  <script lang="ts">
  export default {
    data() {
      return {
        animationDurations: [
          474, 433, 407, 458, 400, 427, 441, 419, 487, 442
        ]
      };
    },
    methods: {
      barStyle(index: number) {
        return {
          left: `${index * 14 + 1}px`,
          animationDuration: `${this.animationDurations[index]}ms`
        };
      }
    }
  };
  </script>
  
  <style scoped>
  html, body {
    height: 100%;
  }
  
  body {
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  #bars {
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .bar {
    background: #52467b;
    bottom: 1px;
    height: 3px;
    width: 10px;
    margin: 0px 4px;
    border-radius: 5px;
    animation: sound 2000ms linear infinite alternate;
  }
  
  @keyframes sound {
    0% {
      opacity: .35;
      height: 3px;
    }
    100% {
      opacity: 1;
      height: 70px;
    }
  }
  </style>