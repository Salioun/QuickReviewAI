<template>
  <div class="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center px-4">

    <!-- Header -->
    <div class="text-center mb-10">
      <h1 class="text-5xl font-bold bg-gradient-to-r from-blue-400 to-violet-400 text-transparent bg-clip-text text-transparent mb-3">
        QuickReview AI
      </h1>
      <p class="text-gray-500 text-lg">
        Analyse automatique de Pull Requests GitHub par IA
      </p>

      <!-- Formulaie -->

      <div class="w-full max-w-2xl">
        <div class="space-y-4">
          <label class="block text-sm font-medium text-gray-300 mb-2">URL du Pull Request</label>
          <input
          v-model="prUrl"
          type="url"
          placeholder="https://github.com/owner/repo/pull/123"
          :disabled="isLoading"
          class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500
                 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                 disabled:opacity-50 disabled:cursor-not-allowed mb-4"
          @keyup.enter="submit"
        />
        <p v-if="errorMessage" class="text-red-400 text-sm mb-4">
          {{ errorMessage }}
        </p>

        <button
          class="w-full bg-gradient-to-r from-blue-500 to-violet-500 text-white rounded-xl py-3 text-lg
                 font-medium hover:from-blue-600 hover:to-violet-600 transition-all duration-200
                 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="isLoading || !prUrl"
          @click="submit"
        >
          <span v-if="!isLoading">Analyser la PR →</span>
          <span v-else class="flex items-center justify-center gap-2">
            <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
            </svg>
            Analyse en cours...
          </span>
        </button>
        </div>

        <!-- Indicateur de progression -->
        <div v-if="reviewId && isPolling" class="mt-6 bg-gray-900 border border-gray-800 rounded-2xl p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="h-2 w-2 rounded-full bg-blue-400 animate-pulse"></div>
            <span class="text-gray-300 text-sm">{{ progressMessage }}</span>
          </div>
          <div class="w-full bg-gray-800 rounded-full h-1.5">
            <div
              class="bg-blue-500 h-1.5 rounded-full transition-all duration-1000"
              :style="{ width: `${progressPercent}%` }"
            ></div>
          </div>
        </div>
      </div>

      <div class="text-center mt-6">
        <NuxtLink to="/history" class="text-gray-500 hover:text-gray-300 text-sm font-mono transition">
          Voir l'historique des reviews →
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup>
const {submitReview, getReview} = useApi()
const router = useRouter()
const prUrl = ref('')
const reviewId = ref(null)
const isPolling = ref(false)
const isLoading = ref(false)
const progressPercent = ref(10)
const errorMessage = ref('')

const PROGRESS_MESSAGES = [
  'Connexion à GitHub...',
  'Récupération du diff...',
  'Analyse du code par l\'IA...',
  'Génération de la review...',
  'Finalisation...',
]

const progressMessage = ref(PROGRESS_MESSAGES[0])


const submit = async () => {
  errorMessage.value = ''

  if (!prUrl.value) return

  isLoading.value = true

  try {
    const data = await submitReview(prUrl.value)
    reviewId.value = data.id
    startPolling(data.id)
  } catch (err) {
    errorMessage.value = err.message
    isLoading.value = false
  }
}

const startPolling = async (id) => {
  isPolling.value = true
  let messageIndex = 0
  let elapsed = 0
  const messageInterval = setInterval(() => {
    messageIndex = Math.min(messageIndex + 1, PROGRESS_MESSAGES.length - 1)
    progressMessage.value = PROGRESS_MESSAGES[messageIndex]
    progressPercent.value = Math.min(progressPercent.value + 18, 90)
  }, 3_000)

  const pollInterval = setInterval(async () => {
    elapsed += 3

    try {
      const review = await getReview(id)
      console.log(review.status)

      if (review.status === 'completed') {
        clearInterval(pollInterval)
        clearInterval(messageInterval)
        // Redirige vers la page de résultats
        router.push(`/reviews/${id}`)
      }

      if (review.status === 'failed') {
        clearInterval(pollInterval)
        clearInterval(messageInterval)
        isLoading.value = false
        isPolling.value = false
        errorMessage.value = 'L\'analyse a échoué. Vérifie que le PR est accessible.'
      }

    } catch {
      // On continue à poller même si une requête échoue
    }

    // Timeout de sécurité après 3 minutes
    if (elapsed >= 180) {
      clearInterval(pollInterval)
      clearInterval(messageInterval)
      isLoading.value = false
      isPolling.value = false
      errorMessage.value = 'Délai dépassé. Réessayer dans quelques instants.'
    }
  }, 3_000)
}
</script>