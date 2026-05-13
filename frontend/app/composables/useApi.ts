export const useApi = () => {
    const config = useRuntimeConfig() // variables d'environnement
    const baseUrl = config.public.apiBase

    const submitReview = async (prUrl:string) => {
        const response = await fetch(`${baseUrl}/reviews/`, {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ pr_url : prUrl})
        })

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.pr_url?.[0] || 'Erreur lors de la soumission');
        }

        return response.json();
    }

    const getReview = async (id:number) => {
        const response = await fetch(`${baseUrl}/reviews/${id}/`)
        
        if (!response.ok) {
            throw new Error('Review introuvable')
        }

        return response.json()
    }

    return {submitReview, getReview}
}