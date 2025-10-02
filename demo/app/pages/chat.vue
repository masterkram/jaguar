<template>
  <div class="w-full h-full">
    <UDashboardPanel class="w-full h-full">
      <div class="flex flex-col justify-between h-full">
        <div class="max-w-4xl mx-auto w-full">
          <div v-for="(m, index) in chat.messages" :key="m.id ? m.id : index">
              {{ m.role === "user" ? "User: " : "AI: " }}
              <div
                  v-for="(part, index) in m.parts"
                  :key="`${m.id}-${part.type}-${index}`"
              >
                  <div v-if="part.type === 'text'">{{ part.text }}</div>
                  <div v-if="part.type === 'tool_call'">
                    Calling {{ part.tool_call.name }}
                  </div>
              </div>
          </div>
        </div>
          <UChatPrompt class="max-w-4xl mx-auto mb-8" variant="subtle" v-model="input" @submit="handleSubmit">
            <UChatPromptSubmit :status="chat.status" />
          </UChatPrompt>
      </div>
    </UDashboardPanel>
  </div>
</template>

<script setup lang="ts">
import { UDashboardPanel } from "#components";
import { Chat } from "@ai-sdk/vue";
import { ref } from "vue";

const input = ref("");
const chat = new Chat({});

const handleSubmit = (e: Event) => {
    e.preventDefault();
    chat.sendMessage({ text: input.value });
    input.value = "";
};
</script>