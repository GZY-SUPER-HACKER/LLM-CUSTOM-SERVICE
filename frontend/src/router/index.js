import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { isLoggedIn } from '../api/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/debug',
      name: 'debug',
      // route level code-splitting
      // this generates a separate chunk (DebugView.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/DebugView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      // route level code-splitting
      // this generates a separate chunk (LoginView.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      // route level code-splitting
      // this generates a separate chunk (RegisterView.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/RegisterView.vue'),
    },
    {
      path: '/admin',
      name: 'admin',
      // route level code-splitting
      // this generates a separate chunk (AdminView.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AdminView.vue'),
      meta: {
        requiresAuth: true
      }
    },
  ],
})

// 导航守卫
router.beforeEach((to, from, next) => {
  // 检查路由是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查是否已登录
    if (!isLoggedIn()) {
      // 未登录，重定向到登录页面
      return next({ name: 'login' })
    } else {
      // 已登录，继续访问
      return next()
    }
  } else {
    // 不需要认证的路由，直接访问
    return next()
  }
})

export default router
