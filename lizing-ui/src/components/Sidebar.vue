<template>
  <aside class="w-64 bg-white shadow p-4">
    <nav class="flex flex-col gap-3">
      <router-link to="/dashboard/new" class="hover:text-teal-600">Создать заявку</router-link>
      <router-link to="/dashboard/leases" class="hover:text-teal-600">Мои заявки</router-link>
      <router-link to="/dashboard/statuses" class="hover:text-teal-600">Статусы</router-link>
      <router-link to="/dashboard/payments" class="hover:text-teal-600">Платежи</router-link>
      <router-link to="/dashboard/profile" class="hover:text-teal-600">Профиль</router-link>
    </nav>
  </aside>
</template>
