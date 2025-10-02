<template>
  <div class="w-full h-full">
    <UContainer class="max-w-4xl py-12">
      <div class="text-center space-y-8">
        <!-- Hero Section -->
        <div class="space-y-4">
          <div class="flex items-center justify-center space-x-3">
            <img src="/logo.png" alt="Jaguar" class="w-16 h-16" />
            <h1 class="text-4xl font-bold text-gray-900 dark:text-white">Jaguar</h1>
          </div>
          <p class="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Upload documents and search through them using powerful command-line tools like ripgrep, jq, and find.
          </p>
          <p class="text-lg text-gray-500 dark:text-gray-500">
            Powered by <a href="https://docs.unstructured.io/" target="_blank" class="text-primary-500 hover:text-primary-600 underline">Unstructured</a> for intelligent document processing.
          </p>
        </div>

        <!-- Quick Actions -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto">
          <UCard class="hover:shadow-lg transition-shadow">
            <div class="text-center space-y-4">
              <div class="w-16 h-16 bg-primary-100 dark:bg-primary-900/20 rounded-full flex items-center justify-center mx-auto">
                <UIcon name="i-heroicons-cloud-arrow-up" class="text-2xl text-primary-600" />
              </div>
              <div>
                <h2 class="text-xl font-semibold">Upload Documents</h2>
                <p class="text-gray-600 dark:text-gray-400 text-sm">
                  Upload PDF, DOCX, TXT, HTML, and many other document formats for processing.
                </p>
              </div>
              <UButton to="/upload" size="lg" class="w-full">
                Get Started
              </UButton>
            </div>
          </UCard>

          <UCard class="hover:shadow-lg transition-shadow">
            <div class="text-center space-y-4">
              <div class="w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center mx-auto">
                <UIcon name="i-heroicons-magnifying-glass" class="text-2xl text-green-600" />
              </div>
              <div>
                <h2 class="text-xl font-semibold">Search Documents</h2>
                <p class="text-gray-600 dark:text-gray-400 text-sm">
                  Use ripgrep for text search, find for file discovery, and jq for metadata queries.
                </p>
              </div>
              <UButton to="/search" variant="outline" size="lg" class="w-full">
                Start Searching
              </UButton>
            </div>
          </UCard>
        </div>

        <!-- Features -->
        <div class="space-y-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white">Features</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="text-center space-y-3">
              <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center mx-auto">
                <UIcon name="i-heroicons-document-text" class="text-xl text-blue-600" />
              </div>
              <div>
                <h3 class="font-medium">Document Processing</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  Intelligent text extraction and markdown conversion using Unstructured
                </p>
              </div>
            </div>

            <div class="text-center space-y-3">
              <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center mx-auto">
                <UIcon name="i-heroicons-bolt" class="text-xl text-purple-600" />
              </div>
              <div>
                <h3 class="font-medium">Fast Search</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  Lightning-fast text search with regex support and context lines
                </p>
              </div>
            </div>

            <div class="text-center space-y-3">
              <div class="w-12 h-12 bg-amber-100 dark:bg-amber-900/20 rounded-lg flex items-center justify-center mx-auto">
                <UIcon name="i-heroicons-code-bracket" class="text-xl text-amber-600" />
              </div>
              <div>
                <h3 class="font-medium">Metadata Queries</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  Query document structure and metadata using powerful JQ expressions
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Stats -->
        <div v-if="stats.totalFiles > 0" class="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
          <h3 class="text-lg font-semibold mb-4">Your Library</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center">
              <div class="text-2xl font-bold text-primary-600">{{ stats.totalFiles }}</div>
              <div class="text-sm text-gray-600 dark:text-gray-400">Documents</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-green-600">{{ stats.processedFiles }}</div>
              <div class="text-sm text-gray-600 dark:text-gray-400">Processed</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-blue-600">{{ stats.totalElements }}</div>
              <div class="text-sm text-gray-600 dark:text-gray-400">Elements</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-600">{{ formatFileSize(stats.totalSize) }}</div>
              <div class="text-sm text-gray-600 dark:text-gray-400">Total Size</div>
            </div>
          </div>
        </div>

        <!-- Getting Started -->
        <div v-else class="bg-gray-50 dark:bg-gray-800 rounded-xl p-8">
          <h3 class="text-lg font-semibold mb-4">Getting Started</h3>
          <div class="space-y-4 text-left max-w-md mx-auto">
            <div class="flex items-start space-x-3">
              <div class="w-6 h-6 bg-primary-100 dark:bg-primary-900/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span class="text-sm font-semibold text-primary-600">1</span>
              </div>
              <div>
                <p class="font-medium">Upload a document</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">Choose from PDF, DOCX, TXT, HTML, and more</p>
              </div>
            </div>
            <div class="flex items-start space-x-3">
              <div class="w-6 h-6 bg-primary-100 dark:bg-primary-900/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span class="text-sm font-semibold text-primary-600">2</span>
              </div>
              <div>
                <p class="font-medium">Wait for processing</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">Unstructured extracts text and metadata</p>
              </div>
            </div>
            <div class="flex items-start space-x-3">
              <div class="w-6 h-6 bg-primary-100 dark:bg-primary-900/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span class="text-sm font-semibold text-primary-600">3</span>
              </div>
              <div>
                <p class="font-medium">Start searching</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">Use ripgrep, find, or jq to explore your content</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </UContainer>
  </div>
</template>

<script setup lang="ts">
const API_BASE_URL = 'http://localhost:8000'

const stats = ref({
  totalFiles: 0,
  processedFiles: 0,
  totalElements: 0,
  totalSize: 0
})

onMounted(async () => {
  await loadStats()
})

async function loadStats() {
  try {
    const response = await fetch(`${API_BASE_URL}/files/`)
    if (response.ok) {
      const data = await response.json()
      const files = data.files || []
      
      stats.value = {
        totalFiles: files.length,
        processedFiles: files.filter((f: any) => f.processing_result?.status === 'success').length,
        totalElements: files.reduce((sum: number, f: any) => sum + (f.processing_result?.element_count || 0), 0),
        totalSize: files.reduce((sum: number, f: any) => sum + (f.size || 0), 0)
      }
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

function formatFileSize(bytes: number): string {
  const sizes = ['B', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 B'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}
</script>