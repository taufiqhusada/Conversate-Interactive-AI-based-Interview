<template>
    <div class="feedback-chat">
      <h4 class="headline">Feedback</h4>
      <div class="chatbox">
        <div class="chat-messages">
          <div v-for="(message, index) in chatMessages" :key="index" class="message">
            <span v-if="message.from === 'user'" class="user-message">{{ message.text }}</span>
            <span v-else class="bot-message">{{ message.text }}</span>
          </div>
        </div>
        <div class="chat-input">
          <input v-model="userMessage" @keyup.enter="sendMessage" placeholder="Type your message..." />
          <button @click="sendMessage">Send</button>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  
  interface ChatMessage {
    text: string;
    from: 'user' | 'bot';
  }
  
  export default defineComponent({
    data() {
      return {
        userMessage: '',
        chatMessages: [] as ChatMessage[], // Define the type for chatMessages
      };
    },
    methods: {
      sendMessage() {
        if (this.userMessage.trim() === '') {
          return;
        }
  
        // Add user message to the chat
        this.chatMessages.push({ text: this.userMessage, from: 'user' });
  
        // Simulate bot response (replace this with your actual chatbot logic)
        this.chatMessages.push({ text: 'Bot response', from: 'bot' });
  
        // Clear the input field after sending the message
        this.userMessage = '';
      },
    },
  });
  </script>
  
  <style scoped>
  .headline {
  text-align: center;
}
.feedback-chat {
  border: 1px solid #ccc;
  background: white;
  height: 50vh;
  padding: 1em;
  display: block;
  right: 0;
  width: 50%;
  height: max-content;
  overflow: auto;
  width: 480px;
  height: fit-content;
  margin: 0 auto 2em auto;
  box-shadow: 2px 2px 5px 2px rgba(0, 0, 0, 0.3);
}
.message {
  width: 90%;
  border-radius: 10px;
  padding: .5em;
  margin-bottom: .5em;
  font-size: .8em;
}
.message-in {
  background: #F1F0F0;
  color: black;
}
  </style>
  