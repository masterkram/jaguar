<template>
  <UApp>
    <UDashboardGroup class="w-full min-h-screen font-mono">
      <UDashboardSidebar>
        <div>
          <img src="/logo.png" alt="Jaguar" class="w-10 h-10" />
          <h1 class="text-2xl font-bold">Jaguar</h1>
        </div>
        <UNavigationMenu orientation="vertical" :items="items" />
      </UDashboardSidebar>
      <NuxtPage />
    </UDashboardGroup>
  </UApp>
</template>

<script setup lang="ts">
const items = [
  {
    label: 'Upload',
    icon: 'i-heroicons-cloud-arrow-up',
    to: '/upload',
  },
  {
    label: 'Search',
    icon: 'i-heroicons-magnifying-glass',
    to: '/search',
  },
  {
    label: 'Chat',
    icon: 'i-heroicons-chat-bubble-left-right',
    to: '/chat',
  },
];
</script>
