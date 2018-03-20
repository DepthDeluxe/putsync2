import Vue from 'vue'
import Router from 'vue-router'

import Downloads from './pages/Downloads.vue'
import History from './pages/History.vue'
import Statistics from './pages/Statistics.vue'
import AddMagnetLink from './pages/AddMagnetLink.vue'
import Configuration from './pages/Configuration.vue'

Vue.use(Router)

export default new Router({
    routes: [
        {
            path: '/',
            name: 'Downloads',
            component: Downloads
        },
        {
            path: '/add',
            name: 'Add',
            component: AddMagnetLink
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
        },
        {
            path: '/configuration',
            name: 'Configuration',
            component: Configuration
        }
    ]
})
