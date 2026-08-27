<template>
    <div class="min-h-screen bg-gray-950 text-white">
  
      <!-- Navbar -->
       <nav class="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <NuxtLink to="/" class="text-blue-400 hover:text-blue-300 flex items-center gap-2 text-sm">
          ← Nouvelle analyse
        </NuxtLink>
        <span class="text-gray-500 text-sm font-mono">QuickReview AI</span>
      </nav>
      
      <!-- Loading -->
      <div v-if="isLoading" class="flex flex-col items-center justify-center h-96 gap-4">
        <svg class="animate-spin h-8 w-8 text-blue-400" viewBox="0 0 24 24" fill="none">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
        </svg>
        <p class="text-gray-400">Chargement de la review...</p>
      </div>
  
      <!-- Erreur -->
      <div v-else-if="error" class="flex flex-col items-center justify-center h-96 gap-4">
        <p class="text-red-400">Une erreur est survenue lors du chargement de la review.</p>
      </div>
  
      <!-- Contenu -->
      <div v-else-if="review" class="max-w-4xl mx-auto px-6 py-12">

        <!-- En-tete -->
         <div class="mb-8">
            <div class="flex items-center gap-3 mb-2">
                <span class="text-gray-300 font-mono text-sm">{{ review.repo_name }} #{{ review.pr_number }}</span>
                <span :class="statusBadgeClass" class="text-xs font-medium px-2.5 py-1 rounded-full">{{ statusLabel }}</span>
            </div>
            <a :href="review.pr_url" target="_blank" class="text-blue-400 hover:underline text-sm">Voir la PR dans Github →</a>
         </div>

        <!-- Score -->
        <div class="bg-gray-900 border border-gray-800 rounded-2xl p-8 mb-6 flex items-center gap-8">
        <div class="text-center">
          <div :class="scoreColorClass" class="text-7xl font-bold">
            {{ review.score }}
          </div>
          <div class="text-gray-500 text-sm mt-1">/ 10</div>
        </div>
        <div>
          <h2 class="text-white font-semibold text-lg mb-2">Résumé</h2>
          <p class="text-gray-300 leading-relaxed">{{ result?.summary }}</p>
        </div>
      </div>

      <!-- Points positifs -->
      <div v-if="result?.positive_points?.length" class="bg-gray-900 border border-green-900 rounded-2xl p-6 mb-6">
        <h3 class="text-green-400 font-semibold mb-4 flex items-center gap-2">
          ✓ Points positifs
        </h3>
        <ul class="space-y-2">
          <li
            v-for="(point, i) in result.positive_points"
            :key="i"
            class="text-gray-300 flex items-start gap-2"
          >
            <span class="text-green-500 mt-0.5">•</span>
            {{ point }}
          </li>
        </ul>
      </div>

      <!-- Bugs -->
      <div v-if="result?.bugs?.length" class="bg-gray-900 border border-red-900 rounded-2xl p-6 mb-6">
        <h3 class="text-red-400 font-semibold mb-4">
          ⚠ Bugs détectés ({{ result.bugs.length }})
        </h3>
        <div class="space-y-4">
          <div
            v-for="(bug, i) in result.bugs"
            :key="i"
            class="border border-gray-800 rounded-xl p-4"
          >
            <div class="flex items-center gap-2 mb-2">
              <span :class="severityClass(bug.severity)" class="text-xs font-bold px-2 py-0.5 rounded">
                {{ bug.severity.toUpperCase() }}
              </span>
              <span class="text-gray-400 font-mono text-sm">{{ bug.file }}</span>
              <span v-if="bug.line" class="text-gray-600 text-xs">ligne {{ bug.line }}</span>
            </div>
            <p class="text-gray-200 mb-2">{{ bug.description }}</p>
            <p class="text-blue-300 text-sm bg-blue-950 rounded-lg px-3 py-2">
              💡 {{ bug.suggestion }}
            </p>
          </div>
        </div>
      </div>

      <!-- Suggestions -->
      <div v-if="result?.suggestions?.length" class="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-6">
        <h3 class="text-yellow-400 font-semibold mb-4">
          ◈ Suggestions ({{ result.suggestions.length }})
        </h3>
        <div class="space-y-4">
          <div
            v-for="(s, i) in result.suggestions"
            :key="i"
            class="border border-gray-800 rounded-xl p-4"
          >
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded font-mono">
                {{ s.category }}
              </span>
              <span class="text-gray-400 font-mono text-sm">{{ s.file }}</span>
            </div>
            <p class="text-gray-200 mb-2">{{ s.description }}</p>
            <p class="text-blue-300 text-sm bg-blue-950 rounded-lg px-3 py-2">
              💡 {{ s.suggestion }}
            </p>
          </div>
        </div>
      </div>

      <!-- Performance -->
      <div v-if="result?.performance?.length" class="bg-gray-900 border border-orange-900 rounded-2xl p-6 mb-6">
        <h3 class="text-orange-400 font-semibold mb-4">
          ⚡ Performance ({{ result.performance.length }})
        </h3>
        <div class="space-y-4">
          <div
            v-for="(p, i) in result.performance"
            :key="i"
            class="border border-gray-800 rounded-xl p-4"
          >
            <span class="text-gray-400 font-mono text-sm block mb-2">{{ p.file }}</span>
            <p class="text-gray-200 mb-2">{{ p.description }}</p>
            <p class="text-blue-300 text-sm bg-blue-950 rounded-lg px-3 py-2">
              💡 {{ p.suggestion }}
            </p>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
const route = useRoute()
const { getReview } = useApi()

const review   = ref(null)
const isLoading = ref(true)
const error    = ref('')

// result_json est le JSON structuré retourné par le LLM
const result = computed(() => review.value?.result_json)

onMounted(async () => {
  try {
    const id = Number(route.params.id)
    review.value = await getReview(id)
  } catch {
    error.value = 'Review introuvable ou inaccessible.'
  } finally {
    isLoading.value = false
  }
})

// --- Helpers d'affichage ---

const statusLabel = computed(() => ({
  pending:    'En attente',
  processing: 'En cours',
  completed:  'Terminée',
  failed:     'Échouée',
}[review.value?.status] ?? ''))

const statusBadgeClass = computed(() => ({
  pending:    'bg-gray-800 text-gray-300',
  processing: 'bg-blue-900 text-blue-300',
  completed:  'bg-green-900 text-green-300',
  failed:     'bg-red-900 text-red-300',
}[review.value?.status] ?? ''))

const scoreColorClass = computed(() => {
  const s = review.value?.score
  if (!s) return 'text-gray-500'
  if (s >= 8) return 'text-green-400'
  if (s >= 5) return 'text-yellow-400'
  return 'text-red-400'
})

const severityClass = (severity) => ({
  critical: 'bg-red-900 text-red-300',
  major:    'bg-orange-900 text-orange-300',
  minor:    'bg-yellow-900 text-yellow-300',
}[severity] ?? 'bg-gray-800 text-gray-300')
</script>