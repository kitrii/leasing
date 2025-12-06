<template>
  <div class="bg-white p-6 rounded-lg shadow-lg">
    <h3 class="text-lg font-bold mb-2">{{ lease.equipment }}</h3>
    <p>Сумма: {{ lease.amount }}</p>
    <p>Статус: <span :class="statusClass">{{ lease.status }}</span></p>
    <p>Создано: {{ lease.created_at }}</p>
  </div>
</template>

<script lang="ts">
export default {
  props: {
    lease: { type: Object, required: true }
  },
  computed: {
    statusClass() {
      return {
        'text-green-600': this.lease.status === 'Одобрена',
        'text-red-600': this.lease.status === 'Отклонена',
        'text-yellow-600': this.lease.status === 'Отправлена'
      }
    }
  }
}
</script>
