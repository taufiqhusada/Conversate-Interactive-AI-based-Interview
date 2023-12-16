
import axios from 'axios';
import fs from 'fs';

export default class GPTService {
    async getTranscriptFromWhisper(audioBlob: Blob) {
        try {
            // Replace 'YOUR_WHISPER_API_KEY' and 'YOUR_WHISPER_API_ENDPOINT' with your actual API key and endpoint
            const apiKey = import.meta.env.VITE_OPEN_AI_KEY;
            const apiUrl = 'https://api.openai.com/v1/audio/transcriptions';

            // Create a FormData object to send the audio file
            const formData = new FormData();
            // Convert the Blob to a File object with the desired filename and type
            const audioFile = new File([audioBlob], 'audio.webm', { type: 'audio/webm' });

            console.log(audioFile, audioFile.name)
            // Append the audio file to the FormData object
            formData.append('file', audioFile, audioFile.name);

            formData.append('model', 'whisper-1');

            console.log(formData);

            // Make an HTTP POST request to the Whisper API
            const response = await axios.post(apiUrl, formData, {
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'multipart/form-data',
                },
            });

            console.log(response);

            // Extract the transcript from the response
            const transcript = response.data.text;

            return transcript;

        } catch (error) {
            console.error('Error getting transcript from Whisper API:', error);
            return '';
        }
    };

    async generateGptResponse(transcript: Array<{ text: string, timeOffset: number, speaker: string }>, instruction: string) {
        try {
            const apiKey = import.meta.env.VITE_OPEN_AI_KEY;


            const messages: Array<{ role: string, content: string}> = transcript.map(item => {
                // You can provide values for the properties as needed
                return {
                  role: item["speaker"].toLowerCase(),
                  content: item["text"],
                };
              });

            messages.push({
                role: 'system',
                content: instruction,
            })

            console.log(messages)
    
            // Define the request payload following the cURL example
            const requestData = {
                model: 'gpt-3.5-turbo',
                messages: messages,
            };

            console.log(requestData)

            // Send the request to the OpenAI API
            const gptResponse = await axios.post('https://api.openai.com/v1/chat/completions', requestData, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`
                }
            });

            const assistantResponse =  gptResponse.data.choices[0].message.content;

            // Generate and play TTS audio from the GPT response
            const audioBuffer = await this.generateTTS(assistantResponse);

            return [audioBuffer, assistantResponse];
        } catch (error) {
            console.error('Error generating GPT response:', error);
            return '';
        }
    };

    // Function to generate TTS audio from text
    async generateTTS(text: string) {
        try {
            // Replace 'YOUR_OPENAI_API_KEY' with your actual OpenAI API key
            const apiKey = import.meta.env.VITE_OPEN_AI_KEY;

            // Send a request to the OpenAI TTS API to generate audio from text
            const ttsResponse = await axios.post('https://api.openai.com/v1/audio/speech', {
                model: 'tts-1',
                input: text,
                voice: 'alloy'
            }, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`
                },
                responseType: 'blob'
            });

            return ttsResponse.data;
        } catch (error) {
            console.error('Error generating TTS audio:', error);
            return null;
        }
    }

}