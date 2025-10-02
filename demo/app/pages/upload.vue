<template>
  <div class="w-full h-full">
    <UContainer class="max-w-4xl py-8">
      <div class="space-y-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white">File Upload</h1>
          <p class="mt-2 text-gray-600 dark:text-gray-400">
            Upload documents to be processed and made searchable. Supports PDF, DOCX, TXT, HTML, and many other formats.
          </p>
        </div>

        <!-- Upload Form -->
        <UCard>
          <template #header>
            <h2 class="text-xl font-semibold">Upload New Document</h2>
          </template>

          <div class="space-y-4">
            <UFormField label="Select File" help="Supported formats: PDF, DOCX, TXT, HTML, Markdown, and more">
              <UInput
                ref="fileInput"
                type="file"
                :accept="acceptedFileTypes"
                @change="handleFileSelect"
                :disabled="isUploading"
              />
            </UFormField>

            <div v-if="selectedFile" class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div class="flex items-center space-x-3">
                <UIcon name="i-heroicons-document" class="text-2xl text-primary-500" />
                <div>
                  <p class="font-medium">{{ selectedFile.name }}</p>
                  <p class="text-sm text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
                </div>
              </div>
              <UButton
                color="red"
                variant="ghost"
                icon="i-heroicons-x-mark"
                @click="clearFile"
                :disabled="isUploading"
              />
            </div>

            <UButton
              @click="uploadFile"
              :loading="isUploading"
              :disabled="!selectedFile"
              class=""
              size="lg"
              icon="i-heroicons-cloud-arrow-up"
            >
              Upload & Process
            </UButton>
          </div>
        </UCard>

        <!-- Upload Status -->
        <UCard v-if="uploadStatus.message" :ui="{ body: { padding: 'p-4' } }">
          <div class="flex items-start space-x-3">
            <UIcon
              :name="uploadStatus.type === 'success' ? 'i-heroicons-check-circle' : uploadStatus.type === 'error' ? 'i-heroicons-x-circle' : 'i-heroicons-information-circle'"
              :class="[
                'text-xl mt-0.5',
                uploadStatus.type === 'success' ? 'text-green-500' : 
                uploadStatus.type === 'error' ? 'text-red-500' : 'text-blue-500'
              ]"
            />
            <div class="flex-1">
              <p :class="[
                'font-medium',
                uploadStatus.type === 'success' ? 'text-green-900 dark:text-green-100' : 
                uploadStatus.type === 'error' ? 'text-red-900 dark:text-red-100' : 'text-blue-900 dark:text-blue-100'
              ]">
                {{ uploadStatus.message }}
              </p>
              <div v-if="uploadResult" class="mt-3 space-y-2">
                <div class="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span class="font-medium">File ID:</span>
                    <span class="ml-2 font-mono text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">{{ uploadResult.file_id }}</span>
                  </div>
                  <div>
                    <span class="font-medium">Elements Found:</span>
                    <span class="ml-2">{{ uploadResult.processing_result?.element_count || 'N/A' }}</span>
                  </div>
                </div>
                <div v-if="uploadResult.processing_result?.content_preview" class="mt-3">
                  <span class="font-medium text-sm">Content Preview:</span>
                  <div class="mt-1 p-3 bg-gray-50 dark:bg-gray-800 rounded text-sm max-h-32 overflow-y-auto">
                    <pre class="whitespace-pre-wrap text-xs">{{ uploadResult.processing_result.content_preview }}</pre>
                  </div>
                </div>
                <div class="flex space-x-2 mt-4">
                  <UButton
                    to="/search"
                    variant="outline"
                    size="sm"
                  >
                    <UIcon name="i-heroicons-magnifying-glass" class="mr-1" />
                    Search This File
                  </UButton>
                  <UButton
                    @click="copyFileId"
                    variant="ghost"
                    size="sm"
                  >
                    <UIcon name="i-heroicons-clipboard-document" class="mr-1" />
                    Copy File ID
                  </UButton>
                </div>
              </div>
            </div>
          </div>
        </UCard>

        <!-- Recent Uploads -->
        <UCard v-if="recentUploads.length > 0">
          <template #header>
            <div class="flex items-center justify-between">
              <h2 class="text-xl font-semibold">Recent Uploads</h2>
              <UButton @click="refreshUploads" variant="ghost" size="sm">
                <UIcon name="i-heroicons-arrow-path" />
              </UButton>
            </div>
          </template>

          <div class="space-y-3">
            <div
              v-for="file in recentUploads"
              :key="file.file_id"
              class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
            >
              <div class="flex items-center space-x-3">
                <UIcon name="i-heroicons-document" class="text-xl text-primary-500" />
                <div>
                  <p class="font-medium">{{ file.original_filename }}</p>
                  <p class="text-sm text-gray-500">
                    {{ formatFileSize(file.size) }} • 
                    {{ file.processing_result?.element_count || 0 }} elements •
                    {{ file.processing_result?.status || 'unknown' }}
                  </p>
                </div>
              </div>
              <div class="flex space-x-2">
                <UButton
                  @click="navigateToSearch(file.file_id)"
                  variant="outline"
                  size="sm"
                >
                  <UIcon name="i-heroicons-magnifying-glass" />
                </UButton>
                <UButton
                  @click="copyFileId(file.file_id)"
                  variant="ghost"
                  size="sm"
                >
                  <UIcon name="i-heroicons-clipboard-document" />
                </UButton>
              </div>
            </div>
          </div>
        </UCard>
      </div>
    </UContainer>
  </div>
</template>

<script setup lang="ts">
interface UploadResult {
  file_id: string
  filename: string
  size: number
  processing_result: {
    status: string
    element_count: number
    content_preview: string
  }
}

interface FileInfo {
  file_id: string
  original_filename: string
  size: number
  processing_result: {
    status: string
    element_count: number
    content_preview: string
  }
}

const API_BASE_URL = 'http://localhost:8000'

const selectedFile = ref<File | null>(null)
const isUploading = ref(false)
const uploadStatus = ref<{ type: 'success' | 'error' | 'info', message: string }>({ type: 'info', message: '' })
const uploadResult = ref<UploadResult | null>(null)
const recentUploads = ref<FileInfo[]>([])
const fileInput = ref()

const acceptedFileTypes = '.pdf,.docx,.doc,.txt,.html,.md,.csv,.xlsx,.pptx,.rtf,.odt,.epub,.eml'

const toast = useToast()

// Load recent uploads on mount
onMounted(() => {
  loadRecentUploads()
})

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
    uploadStatus.value = { type: 'info', message: '' }
    uploadResult.value = null
  }
}

function clearFile() {
  selectedFile.value = null
  uploadStatus.value = { type: 'info', message: '' }
  uploadResult.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function uploadFile() {
  if (!selectedFile.value) return

  isUploading.value = true
  uploadStatus.value = { type: 'info', message: 'Uploading and processing file...' }

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await fetch(`${API_BASE_URL}/upload/`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`)
    }

    const result: UploadResult = await response.json()
    uploadResult.value = result

    if (result.processing_result?.status === 'success') {
      uploadStatus.value = {
        type: 'success',
        message: 'File uploaded and processed successfully!'
      }
      toast.add({
        title: 'Upload Successful',
        description: `${result.filename} has been processed and is ready for search.`,
        color: 'success'
      })
    } else {
      uploadStatus.value = {
        type: 'error',
        message: `Processing failed: ${result.processing_result?.error || 'Unknown error'}`
      }
    }

    // Refresh the recent uploads list
    await loadRecentUploads()
    
    // Clear the form
    clearFile()

  } catch (error) {
    console.error('Upload error:', error)
    uploadStatus.value = {
      type: 'error',
      message: `Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    }
    toast.add({
      title: 'Upload Failed',
      description: 'There was an error uploading your file. Please try again.',
      color: 'error'
    })
  } finally {
    isUploading.value = false
  }
}

async function loadRecentUploads() {
  try {
    const response = await fetch(`${API_BASE_URL}/files/`)
    if (response.ok) {
      const data = await response.json()
      recentUploads.value = data.files.slice(0, 5) // Show only the 5 most recent
    }
  } catch (error) {
    console.error('Failed to load recent uploads:', error)
  }
}

async function refreshUploads() {
  await loadRecentUploads()
  toast.add({
    title: 'Refreshed',
    description: 'Recent uploads have been updated.',
    color: 'info'
  })
}

function formatFileSize(bytes: number): string {
  const sizes = ['B', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 B'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

async function copyFileId(fileId?: string) {
  const id = fileId || uploadResult.value?.file_id
  if (id) {
    await navigator.clipboard.writeText(id)
    toast.add({
      title: 'Copied',
      description: 'File ID copied to clipboard.',
      color: 'info'
    })
  }
}

function navigateToSearch(fileId: string) {
  navigateTo(`/search?file_id=${fileId}`)
}
</script>