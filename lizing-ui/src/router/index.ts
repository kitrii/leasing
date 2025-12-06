import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
// import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import NewLease from '../views/NewLease.vue'
import MyLeases from '../views/MyLeases.vue'
import Statuses from '../views/Statuses.vue'
import Payments from '../views/Payments.vue'
import Profile from '../views/Profile.vue'

const routes: RouteRecordRaw[] = [
//   { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/dashboard', component: Dashboard,
    children: [
      { path: 'new', component: NewLease },
      { path: 'leases', component: MyLeases },
      { path: 'statuses', component: Statuses },
      { path: 'payments', component: Payments },
      { path: 'profile', component: Profile },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
