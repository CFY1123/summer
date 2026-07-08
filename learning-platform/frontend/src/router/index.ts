import { createRouter, createWebHistory } from 'vue-router';
import AppLayout from '../layout/AppLayout.vue';
import { useAuthStore } from '../stores/auth';
import { updatePageSeo } from '../utils/seo';

const HomePage = () => import('../pages/home/HomePage.vue');
const LearningRoadmapPage = () => import('../pages/learning-roadmap/LearningRoadmapPage.vue');
const LearningWorkbenchPage = () => import('../pages/learning-workbench/LearningWorkbenchPage.vue');
const SuggestionsCommentsPage = () => import('../pages/suggestions-comments/SuggestionsCommentsPage.vue');
const InterviewQuestionsPage = () => import('../pages/interview-questions/InterviewQuestionsPage.vue');
const PracticeAgentPage = () => import('../pages/practice-agent/PracticeAgentPage.vue');
const ProfilePage = () => import('../pages/profile/ProfilePage.vue');

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        { path: '', redirect: '/home' },
        {
          path: 'home',
          name: 'home',
          component: HomePage,
          meta: { title: 'AI StudyHub', canonicalPath: '/home', structuredDataType: 'WebPage' },
        },
        {
          path: 'learning-roadmap',
          name: 'learning-roadmap',
          component: LearningRoadmapPage,
          meta: { title: 'Learning Roadmap', canonicalPath: '/learning-roadmap', structuredDataType: 'LearningResource' },
        },
        {
          path: 'learning-workbench',
          name: 'learning-workbench',
          component: LearningWorkbenchPage,
          meta: { title: 'Learning Workbench', canonicalPath: '/learning-workbench', structuredDataType: 'LearningResource' },
        },
        {
          path: 'suggestions-comments',
          name: 'suggestions-comments',
          component: SuggestionsCommentsPage,
          meta: { title: 'Suggestions', canonicalPath: '/suggestions-comments', structuredDataType: 'DiscussionForumPosting' },
        },
        {
          path: 'interview-questions',
          name: 'interview-questions',
          component: InterviewQuestionsPage,
          meta: { title: 'Interview Questions', canonicalPath: '/interview-questions', structuredDataType: 'LearningResource' },
        },
        {
          path: 'practice-agent',
          name: 'practice-agent',
          component: PracticeAgentPage,
          meta: { title: 'AI Practice', canonicalPath: '/practice-agent', structuredDataType: 'LearningResource', keepAlive: true },
        },
        {
          path: 'profile',
          name: 'profile',
          component: ProfilePage,
          meta: { title: 'Profile', requiresAuth: true, noIndex: true },
        },
      ],
    },
    { path: '/home', redirect: '/' },
  ],
});

router.beforeEach(async (to) => {
  const authStore = useAuthStore();
  await authStore.initialize();

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return {
      path: '/home',
      query: {
        loginGuide: '1',
        redirect: to.fullPath,
      },
    };
  }
  return true;
});

router.afterEach((to) => {
  updatePageSeo(to);
});

export default router;
