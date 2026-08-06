<template>
<div class="min-h-screen bg-gray-950 text-white">

    <!-- Navbar -->
    <nav class="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <NuxtLink to="/" class="text-blue-400 hover:text-blue-300 flex items-center gap-2 text-sm">
          ← Nouvelle analyse
        </NuxtLink>
        <span class="text-gray-500 text-sm font-mono">Historique</span>
    </nav>

    <!-- Entête -->
     <div class="max-w-4xl mx-auto px-6 py-10">
            <h1 class="text-2xl font-bold mb-8"> Reviews récentes</h1>

            <div v-if="isLoading" class="text-gray-500 text-center py-20">Chargement</div>

            <div v-else-if="reviews.length === 0" class="text-gray-500 text-center py-20">Aucune review pour l'instant.</div>

            <div v-else class="space-y-3">
                <NuxtLink
                    v-for="review in reviews"
                    :key ="review.id"
                    :to="`reviews/${review.id}`"
                    class="block bg-gray-900 border border-gray-800 hover:border-gray-600 rounded-xl p-5 transition-colors"
                >
                    <div class="flex items-center justify-between">
                        <div>
                            <span class="font-mono text-sm text-gray-300"> {{ review.repo_name }}</span>
                            <span class="text-gray-600 text-sm ml-2"> #{{ review.pr_number }}</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <span v-if="review.score" class="font-bold text-3xl" :class="scoreColorClass(review.score)" >
                                {{ review.score }}
                            </span>
                            <span class="text-sm text-gray-600"> /10</span>
                            <span :class="statusColor(review.status)" class="text-xs px-2 py-1 rounded-full font-mono">{{ review.status }}</span>
                        </div>
                    </div>
                    <p class="text-gray-500 text-xs mt-2">
                        {{ new Date(review.created_at).toLocaleDateString('fr-CA', {
                        day: 'numeric', month: 'long', year: 'numeric',
                        hour: '2-digit', minute: '2-digit'
                        }) }}
                    </p>
                </NuxtLink>
            </div>
     </div>

</div>
</template>

<script setup>


const {getReviews} = useApi()
const reviews = ref([])
const isLoading = ref(true)

onMounted(async () => {
    try {
        reviews.value = await getReviews()
    } finally {
        isLoading.value = false
    }
})

const scoreColorClass = (score) => {
  if (score >= 8) return 'text-green-400'
  if (score >= 5) return 'text-yellow-400'
  return 'text-red-400'
}

const statusColor = (status) => ({
  pending:    'bg-gray-800 text-gray-300',
  processing: 'bg-blue-900 text-blue-300',
  completed:  'bg-green-900 text-green-300',
  failed:     'bg-red-900 text-red-300',
}[status] ?? '')



</script>