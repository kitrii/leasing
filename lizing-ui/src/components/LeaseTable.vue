<template>
  <table class="min-w-full border-collapse border border-gray-300">
    <thead class="bg-teal-100">
      <tr>
        <th class="border px-2 py-1">ID</th>
        <th class="border px-2 py-1">Оборудование</th>
        <th class="border px-2 py-1">Сумма</th>
        <th class="border px-2 py-1">Статус</th>
        <th class="border px-2 py-1">Дата</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="lease in leases" :key="lease.id" class="hover:bg-gray-50">
        <td class="border px-2 py-1">{{ lease.id }}</td>
        <td class="border px-2 py-1">{{ lease.equipment }}</td>
        <td class="border px-2 py-1">{{ lease.amount }}</td>
        <td class="border px-2 py-1">{{ lease.status }}</td>
        <td class="border px-2 py-1">{{ lease.created_at }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script lang="ts" setup>
defineProps<{ leases: any[] }>()
</script>
