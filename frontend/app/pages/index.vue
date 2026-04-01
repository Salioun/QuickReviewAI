<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="bg-white rounded-xl shadow-sm border p-8 w-full max-w-lg">
      <h1 class="text-2xl font-semibold text-gray-900 mb-2">
        QuickReview AI
      </h1>
      <p class="text-gray-500 mb-6 text-sm">
        Colle l'URL d'un Pull Request GitHub pour obtenir une code review automatique.
      </p>

      <div class="space-y-4">
        <input
          v-model="prUrl"
          type="text"
          placeholder="https://github.com/owner/repo/pull/123"
          class="w-full border border-gray-200 rounded-lg px-4 py-3 text-sm
                 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          class="w-full bg-gray-900 text-white rounded-lg py-3 text-sm
                 font-medium hover:bg-gray-700 transition-colors"
          @click="submit"
        >
          Analyser la PR
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const prUrl = ref('')

function submit() {
  // Phase 3 — pour l'instant juste un log
  console.log('URL soumise :', prUrl.value)
}
</script>