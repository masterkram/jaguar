<template>
  <div class="flex flex-col min-h-screen w-full">
    <UContainer class="max-w-6xl py-8 flex-1 overflow-y-auto">
      <div class="space-y-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Search Documents</h1>
          <p class="mt-2 text-gray-600 dark:text-gray-400">
            Search through your uploaded documents using powerful command-line tools.
          </p>
        </div>

        <!-- Search Controls -->
        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <h2 class="text-xl font-semibold">Search Settings</h2>
              <USelectMenu
                v-model="selectedTool"
                :items="searchTools"
                option-attribute="label"
                value-attribute="value"
              >
                <template #label>
                  <UIcon :name="getToolIcon(selectedTool)" class="mr-2" />
                  {{ getToolLabel(selectedTool) }}
                </template>
              </USelectMenu>
            </div>
          </template>

          <div class="space-y-4">
            <!-- File Selection -->
            <UFormField label="Search Scope">
              <USelectMenu
                class="h-6"
                v-model="selectedFileId"
                :items="fileOptions"
                placeholder="All files"
                option-attribute="label"
                value-attribute="value"
                :loading="loadingFiles"
                @click="loadFiles"
              />
            </UFormField>

            <!-- Ripgrep Search -->
            <div v-if="selectedTool === 'ripgrep'" class="space-y-4">
              <UFormField label="Search Pattern" help="Enter text or regex pattern to search for">
                <UInput
                  v-model="ripgrepParams.pattern"
                  placeholder="e.g., machine learning, neural.*network"
                  @keyup.enter="performSearch"
                />
              </UFormField>
              <div class="grid grid-cols-2 gap-4">
                <UFormField label="Context Lines" help="Number of lines to show around matches">
                  <UInput
                    v-model.number="ripgrepParams.context"
                    type="number"
                    min="0"
                    max="10"
                    placeholder="0"
                  />
                </UFormField>
                <UFormField label="Options">
                  <UCheckbox
                    v-model="ripgrepParams.caseSensitive"
                    label="Case sensitive"
                  />
                </UFormField>
              </div>
            </div>

            <!-- Find Search -->
            <div v-else-if="selectedTool === 'find'" class="space-y-4">
              <div class="grid grid-cols-3 gap-4">
                <UFormGroup label="Name Pattern" help="File name pattern (e.g., *.md)">
                  <UInput
                    v-model="findParams.namePattern"
                    placeholder="*.md"
                  />
                </UFormGroup>
                <UFormGroup label="File Type">
                  <USelectMenu
                    v-model="findParams.fileType"
                    :items="[
                      { label: 'Any', value: '' },
                      { label: 'Files', value: 'f' },
                      { label: 'Directories', value: 'd' }
                    ]"
                    option-attribute="label"
                    value-attribute="value"
                  />
                </UFormGroup>
                <UFormGroup label="Size Filter" help="e.g., +1M, -100k">
                  <UInput
                    v-model="findParams.size"
                    placeholder="+1M"
                  />
                </UFormGroup>
              </div>
            </div>

            <!-- JQ Search -->
            <div v-else-if="selectedTool === 'jq'" class="space-y-4">
              <UFormGroup label="File ID" help="Select a specific file to query its metadata">
                <USelectMenu
                  v-model="jqParams.fileId"
                  :options="fileOptions.filter((f: FileOption) => f.value)"
                  placeholder="Select a file"
                  option-attribute="label"
                  value-attribute="value"
                  :required="true"
                />
              </UFormGroup>
              <UFormGroup label="JQ Filter Expression" help="Enter JQ expression to query JSON metadata">
                <UInput
                  v-model="jqParams.filter"
                  placeholder="e.g., length, .[].metadata.page_number, .[] | select(.category == &quot;Title&quot;)"
                  @keyup.enter="performSearch"
                />
              </UFormGroup>
              <div class="text-sm text-gray-600 dark:text-gray-400">
                <p class="font-medium mb-1">Common JQ queries:</p>
                <ul class="space-y-1 text-xs">
                  <li><code class="bg-gray-100 dark:bg-gray-800 px-1 rounded">length</code> - Count total elements</li>
                  <li><code class="bg-gray-100 dark:bg-gray-800 px-1 rounded">.[].category</code> - List all element categories</li>
                  <li><code class="bg-gray-100 dark:bg-gray-800 px-1 rounded">.[] | select(.category == "Title")</code> - Filter by element type</li>
                </ul>
              </div>
            </div>

            <UButton
              @click="performSearch"
              :loading="isSearching"
              :disabled="!canSearch"
              size="lg"
              :icon="getToolIcon(selectedTool)"
            >
              Search
            </UButton>
          </div>
        </UCard>

        <!-- Search Results -->
        <UCard v-if="searchResults.length > 0 || searchError">
          <template #header>
            <div class="flex items-center justify-between">
              <h2 class="text-xl font-semibold">
                Search Results
                <span v-if="searchStats.totalMatches !== undefined" class="text-sm text-gray-500 ml-2">
                  ({{ searchStats.totalMatches }} matches)
                </span>
              </h2>
              <div class="flex items-center space-x-2">
                <UButton
                  @click="exportResults"
                  variant="outline"
                  size="sm"
                  :disabled="searchResults.length === 0"
                >
                  <UIcon name="i-heroicons-arrow-down-tray" />
                  Export
                </UButton>
                <UButton
                  @click="clearResults"
                  variant="ghost"
                  size="sm"
                >
                  <UIcon name="i-heroicons-x-mark" />
                  Clear
                </UButton>
              </div>
            </div>
          </template>

          <!-- Error Display -->
          <div v-if="searchError" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <div class="flex items-start space-x-3">
              <UIcon name="i-heroicons-x-circle" class="text-red-500 text-xl mt-0.5" />
              <div>
                <p class="font-medium text-red-900 dark:text-red-100">Search Error</p>
                <p class="text-red-700 dark:text-red-300 text-sm mt-1">{{ searchError }}</p>
              </div>
            </div>
          </div>

          <!-- Results Display -->
          <div v-else-if="searchResults.length > 0" class="space-y-4">
            <!-- Ripgrep Results -->
            <div v-if="selectedTool === 'ripgrep'" class="space-y-3">
              <div
                v-for="(result, index) in searchResults"
                :key="index"
                class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
              >
                <div v-if="result.type === 'match'" class="space-y-2">
                  <div class="flex items-center justify-between">
                    <div class="text-sm text-gray-600 dark:text-gray-400">
                      <span class="font-mono">{{ result.data?.path?.text || 'Unknown file' }}</span>
                      <span class="mx-2">•</span>
                      <span>Line {{ result.data?.line_number }}</span>
                    </div>
                    <UButton
                      @click="copyText(result.data?.lines?.text)"
                      variant="ghost"
                      size="xs"
                    >
                      <UIcon name="i-heroicons-clipboard-document" />
                    </UButton>
                  </div>
                  <div class="bg-gray-50 dark:bg-gray-800 rounded p-3">
                    <pre class="text-sm whitespace-pre-wrap">{{ result.data?.lines?.text }}</pre>
                  </div>
                </div>
              </div>
            </div>

            <!-- Find Results -->
            <div v-else-if="selectedTool === 'find'" class="space-y-2">
              <div
                v-for="(file, index) in searchResults"
                :key="index"
                class="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
              >
                <div class="flex items-center space-x-3">
                  <UIcon name="i-heroicons-document" class="text-primary-500" />
                  <span class="font-mono text-sm">{{ file }}</span>
                </div>
                <UButton
                  @click="copyText(file)"
                  variant="ghost"
                  size="xs"
                >
                  <UIcon name="i-heroicons-clipboard-document" />
                </UButton>
              </div>
            </div>

            <!-- JQ Results -->
            <div v-else-if="selectedTool === 'jq'" class="space-y-3">
              <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Query Result</span>
                  <UButton
                    @click="copyText(JSON.stringify(jqResult, null, 2))"
                    variant="ghost"
                    size="xs"
                  >
                    <UIcon name="i-heroicons-clipboard-document" />
                  </UButton>
                </div>
                <pre class="text-sm whitespace-pre-wrap bg-white dark:bg-gray-900 p-3 rounded border overflow-x-auto">{{ JSON.stringify(jqResult, null, 2) }}</pre>
              </div>
            </div>
          </div>

          <!-- No Results -->
          <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
            <UIcon name="i-heroicons-magnifying-glass" class="text-4xl mb-3" />
            <p>No results found. Try adjusting your search parameters.</p>
          </div>
        </UCard>

        <!-- Quick Actions -->
        <UCard>
          <template #header>
            <h2 class="text-xl font-semibold">Quick Actions</h2>
          </template>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <UButton
              @click="quickSearch('machine learning')"
              variant="outline"
              class="justify-start"
            >
              <UIcon name="i-heroicons-academic-cap" class="mr-2" />
              Search "machine learning"
            </UButton>
            <UButton
              @click="quickSearch('data')"
              variant="outline"
              class="justify-start"
            >
              <UIcon name="i-heroicons-chart-bar" class="mr-2" />
              Search "data"
            </UButton>
            <UButton
              @click="quickJqQuery('length')"
              variant="outline"
              class="justify-start"
            >
              <UIcon name="i-heroicons-hashtag" class="mr-2" />
              Count elements
            </UButton>
          </div>
        </UCard>
      </div>
    </UContainer>
  </div>
</template>

<script setup lang="ts">
interface FileOption {
  label: string
  value: string
}

interface SearchResult {
  type?: string
  data?: any
  [key: string]: any
}

const API_BASE_URL = 'http://localhost:8000'

const route = useRoute()
const toast = useToast()

// Search tool selection
const selectedTool = ref('ripgrep')
const searchTools = [
  { label: 'Ripgrep (Text Search)', value: 'ripgrep' },
  { label: 'Find (File Search)', value: 'find' },
  { label: 'JQ (JSON Query)', value: 'jq' }
]

// File selection
const selectedFileId = ref('')
const fileOptions = ref<FileOption[]>([{ label: 'All files', value: '' }])
const loadingFiles = ref(false)

// Search parameters
const ripgrepParams = ref({
  pattern: '',
  context: 0,
  caseSensitive: false
})

const findParams = ref({
  namePattern: '',
  fileType: '',
  size: ''
})

const jqParams = ref({
  fileId: '',
  filter: ''
})

// Search state
const isSearching = ref(false)
const searchResults = ref<SearchResult[]>([])
const searchError = ref('')
const searchStats = ref<{ totalMatches?: number }>({})
const jqResult = ref<any>(null)

// Load file ID from query parameter if provided
onMounted(() => {
  if (route.query.file_id) {
    selectedFileId.value = route.query.file_id as string
    jqParams.value.fileId = route.query.file_id as string
  }
  loadFiles()
})

const canSearch = computed(() => {
  switch (selectedTool.value) {
    case 'ripgrep':
      return ripgrepParams.value.pattern.trim() !== ''
    case 'find':
      return ripgrepParams.value.pattern || findParams.value.namePattern || findParams.value.fileType || findParams.value.size
    case 'jq':
      return jqParams.value.fileId && jqParams.value.filter.trim() !== ''
    default:
      return false
  }
})

async function loadFiles() {
  loadingFiles.value = true
  try {
    const response = await fetch(`${API_BASE_URL}/files/`)
    if (response.ok) {
      const data = await response.json()
      fileOptions.value = [
        { label: 'All files', value: '' },
        ...data.files.map((file: any) => ({
          label: `${file.original_filename} (${file.file_id.slice(0, 8)}...)`,
          value: file.file_id
        }))
      ]
    }
  } catch (error) {
    console.error('Failed to load files:', error)
  } finally {
    loadingFiles.value = false
  }
}

async function performSearch() {
  if (!canSearch.value) return

  isSearching.value = true
  searchError.value = ''
  searchResults.value = []
  searchStats.value = {}
  jqResult.value = null

  try {
    let response: Response

    switch (selectedTool.value) {
      case 'ripgrep':
        response = await performRipgrepSearch()
        break
      case 'find':
        response = await performFindSearch()
        break
      case 'jq':
        response = await performJqSearch()
        break
      default:
        throw new Error('Unknown search tool')
    }

    if (!response.ok) {
      throw new Error(`Search failed: ${response.statusText}`)
    }

    const result = await response.json()
    
    if (selectedTool.value === 'ripgrep') {
      searchResults.value = result.results || []
      searchStats.value.totalMatches = result.total_matches
    } else if (selectedTool.value === 'find') {
      searchResults.value = result.results || []
    } else if (selectedTool.value === 'jq') {
      jqResult.value = result.result
    }

    toast.add({
      title: 'Search Complete',
      description: `Found ${searchResults.value.length || (jqResult.value ? 1 : 0)} result(s)`,
      color: 'success'
    })

  } catch (error) {
    console.error('Search error:', error)
    searchError.value = error instanceof Error ? error.message : 'Unknown search error'
    toast.add({
      title: 'Search Failed',
      description: 'There was an error performing the search.',
      color: 'error'
    })
  } finally {
    isSearching.value = false
  }
}

async function performRipgrepSearch(): Promise<Response> {
  const params = new URLSearchParams({
    pattern: ripgrepParams.value.pattern,
    case_sensitive: ripgrepParams.value.caseSensitive.toString(),
    context: ripgrepParams.value.context.toString()
  })

  if (selectedFileId.value) {
    params.append('file_id', selectedFileId.value)
  }

  return fetch(`${API_BASE_URL}/search/ripgrep/?${params}`)
}

async function performFindSearch(): Promise<Response> {
  const params = new URLSearchParams()

  if (findParams.value.namePattern) {
    params.append('name_pattern', findParams.value.namePattern)
  }
  if (findParams.value.fileType) {
    params.append('file_type', findParams.value.fileType)
  }
  if (findParams.value.size) {
    params.append('size', findParams.value.size)
  }

  return fetch(`${API_BASE_URL}/search/find/?${params}`)
}

async function performJqSearch(): Promise<Response> {
  const params = new URLSearchParams({
    file_id: jqParams.value.fileId,
    jq_filter: jqParams.value.filter
  })

  return fetch(`${API_BASE_URL}/search/jq/?${params}`)
}

function quickSearch(pattern: string) {
  selectedTool.value = 'ripgrep'
  ripgrepParams.value.pattern = pattern
  ripgrepParams.value.context = 1
  ripgrepParams.value.caseSensitive = false
  performSearch()
}

function quickJqQuery(filter: string) {
  selectedTool.value = 'jq'
  jqParams.value.filter = filter
  if (fileOptions.value.length > 1 && !jqParams.value.fileId) {
    jqParams.value.fileId = fileOptions.value[1]?.value || ''
  }
  if (jqParams.value.fileId) {
    performSearch()
  } else {
    toast.add({
      title: 'No Files Available',
      description: 'Please upload a file first before using JQ queries.',
      color: 'warning'
    })
  }
}

function clearResults() {
  searchResults.value = []
  searchError.value = ''
  searchStats.value = {}
  jqResult.value = null
}

async function copyText(text: string) {
  if (text) {
    await navigator.clipboard.writeText(text)
    toast.add({
      title: 'Copied',
      description: 'Text copied to clipboard.',
      color: 'info'
    })
  }
}

function exportResults() {
  let data: any
  let filename: string

  if (selectedTool.value === 'jq') {
    data = jqResult.value
    filename = `jq-query-results-${Date.now()}.json`
  } else {
    data = searchResults.value
    filename = `${selectedTool.value}-search-results-${Date.now()}.json`
  }

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)

  toast.add({
    title: 'Exported',
    description: 'Search results have been downloaded.',
    color: 'success'
  })
}

function getToolIcon(tool: string): string {
  switch (tool) {
    case 'ripgrep':
      return 'i-heroicons-magnifying-glass'
    case 'find':
      return 'i-heroicons-folder'
    case 'jq':
      return 'i-heroicons-code-bracket'
    default:
      return 'i-heroicons-magnifying-glass'
  }
}

function getToolLabel(tool: string): string {
  const toolObj = searchTools.find(t => t.value === tool)
  return toolObj?.label || 'Unknown'
}
</script>