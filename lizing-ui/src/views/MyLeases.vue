<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">Мои заявки</h2>

    <div class="flex gap-3 mb-4">
      <select v-model="status" @change="loadLeases" class="border p-2 rounded">
        <option value="all">Все</option>
        <option value="Отправлена">Отправлена</option>
        <option value="Одобрена">Одобрена</option>
        <option value="Отклонена">Отклонена</option>
      </select>

      <select v-model="order" @change="loadLeases" class="border p-2 rounded">
        <option value="desc">Сначала новые</option>
        <option value="asc">Сначала старые</option>
      </select>
    </div>

    <LeaseTable :leases="leases" />

    <Loader v-if="loading" />
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import LeaseTable from '../components/LeaseTable.vue'
import Loader from '../components/Loader.vue'

const leases = ref([])
const status = ref('all')
const order = ref('desc')
const loading = ref(false)

async function loadLeases() {
  loading.value = true
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/leases/list?status=${status.value}&order=${order.value}`)
    const data = await res.json()
    leases.value = data.leases
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(loadLeases)
</script>
