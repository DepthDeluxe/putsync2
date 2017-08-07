import Vue from 'vue'
import Router from 'vue-router'

import Downloads from './components/Downloads.vue'
import History from './components/History.vue'
import Statistics from './components/Statistics.vue'

Vue.use(Router)

export default new Router({
    routes: [
        {
            path: '/',
            name: 'Downloads',
            component: Downloads
        },
        {
            path: '/history',
            name: 'History',
            component: History
        },
        {
            path: '/statistics',
            name: 'Statistics',
            component: Statistics
        }
    ]
})
