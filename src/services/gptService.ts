
import axios from 'axios';
import fs from 'fs';

export interface Subtitle {
    number: string;
    startTime: number;
    endTime: number;
    text: string;
}

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

            formData.append('language', 'en');
            formData.append('response_format', 'srt');


            // Make an HTTP POST request to the Whisper API
            const response = await axios.post(apiUrl, formData, {
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'multipart/form-data',
                },
            });

            console.log(response);

            // Extract the transcript from the response
            const transcript = response.data;
            console.log(transcript);

            return this.extractSubtitles(transcript);

        } catch (error) {
            console.error('Error getting transcript from Whisper API:', error);
            return [];
        }
    };

    async generateGptResponse(transcript: Array<{ text: string, timeOffset: number, speaker: string }>, instruction: string) {
        try {
            const apiKey = import.meta.env.VITE_OPEN_AI_KEY;


            const messages: Array<{ role: string, content: string }> = transcript.map(item => {
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

            const assistantResponse = gptResponse.data.choices[0].message.content;

            // Generate and play TTS audio from the GPT response
            const audioBuffer = await this.generateTTS(assistantResponse);

            return [audioBuffer, assistantResponse];
        } catch (error) {
            console.error('Error generating GPT response:', error);
            return '';
        }
    };

    async extractSubtitles(strSubtitle: String) {
        const subtitleBlocks = strSubtitle.trim().split('\n\n')
        console.log(subtitleBlocks);

        // Initialize an array to store the parsed subtitles
        const subtitles: Subtitle[] = [];

        // Iterate through each subtitle block
        subtitleBlocks.forEach((block) => {
            // Split the block into lines
            const lines = block.trim().split('\n');

            // Extract the subtitle number (e.g., "1")
            const subtitleNumber = lines[0];

            // Extract the subtitle timing (e.g., "00:00:05,000 --> 00:00:10,000")
            const timing = lines[1];

            // Extract the subtitle text (remaining lines)
            const text = lines.slice(2).join('\n');

            // Split the timing into start and end times
            let [startTime, endTime] = timing.split(' --> ');

            // Create a subtitle object with parsed data
            const subtitle = {
                number: subtitleNumber,
                startTime: this.srtTimeToSeconds(startTime),
                endTime: this.srtTimeToSeconds(endTime),
                text,
            };

            // Push the subtitle object to the subtitles array
            subtitles.push(subtitle);
        });

        return subtitles;
    }

    srtTimeToSeconds(srtTime: string) {
        // Split the time into parts: hours, minutes, seconds, and milliseconds
        const parts = srtTime.replace(',', '.').split(':');

        // Extract hours, minutes, seconds, and milliseconds
        const hours = parseInt(parts[0], 10);
        const minutes = parseInt(parts[1], 10);
        const seconds = parseFloat(parts[2]);
        const milliseconds = parts[3] ? parseFloat(parts[3]) : 0;

        // Calculate the total duration in seconds
        const totalSeconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000;

        return totalSeconds;
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