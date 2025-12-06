<template>
  <div class="flex flex-col min-h-screen">
    <header class="bg-teal-600 text-white p-4 flex justify-between items-center">
      <h1 class="text-xl font-bold">Личный кабинет</h1>
      <button class="bg-red-500 px-3 py-1 rounded" @click="logout">Выйти</button>
    </header>

    <div class="flex flex-1">
      <aside class="w-64 bg-white shadow p-4 flex flex-col gap-3">
        <router-link to="/dashboard/new" class="hover:text-teal-600">Создать заявку</router-link>
        <router-link to="/dashboard/leases" class="hover:text-teal-600">Мои заявки</router-link>
        <router-link to="/dashboard/statuses" class="hover:text-teal-600">Статусы</router-link>
        <router-link to="/dashboard/payments" class="hover:text-teal-600">Платежи</router-link>
        <router-link to="/dashboard/profile" class="hover:text-teal-600">Профиль</router-link>
      </aside>

      <main class="flex-1 p-6 bg-gray-100">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script lang="ts" setup>
const logout = () => {
  localStorage.removeItem('token')
  window.location.href = '/'
}
</script>
