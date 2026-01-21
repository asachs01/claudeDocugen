// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://asachs01.github.io',
	base: '/claudeDocugen',
	integrations: [
		starlight({
			title: 'DocuGen',
			description: 'AI-powered documentation generator for web workflows',
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/asachs01/claudeDocugen' },
			],
			editLink: {
				baseUrl: 'https://github.com/asachs01/claudeDocugen/edit/main/docs/',
			},
			expressiveCode: {
				themes: ['github-light', 'github-dark'],
				styleOverrides: {
					// Make code blocks more readable
					codeBg: '#1e293b',
					codeSelectionBg: '#475569',
					borderColor: '#475569',
					frames: {
						terminalBackground: '#0f172a',
						terminalTitlebarBackground: '#1e293b',
						terminalTitlebarBorderBottom: '#475569',
					},
				},
			},
			sidebar: [
				{
					label: 'Getting Started',
					items: [
						{ label: 'Quick Start', slug: 'getting-started' },
						{ label: 'Installation', slug: 'getting-started/installation' },
						{ label: 'Your First Workflow', slug: 'getting-started/first-workflow' },
					],
				},
				{
					label: 'Guides',
					items: [
						{ label: 'Recording Workflows', slug: 'guides/recording' },
						{ label: 'Screenshot Annotation', slug: 'guides/annotation' },
						{ label: 'Using Templates', slug: 'guides/templates' },
						{ label: 'Audience Adaptation', slug: 'guides/audiences' },
					],
				},
				{
					label: 'Reference',
					items: [
						{ label: 'Skill API', slug: 'reference/skill-api' },
						{ label: 'Python Scripts', slug: 'reference/scripts' },
						{ label: 'Configuration', slug: 'reference/configuration' },
					],
				},
				{
					label: 'Developers',
					items: [
						{ label: 'Architecture', slug: 'developers/architecture' },
						{ label: 'Extending DocuGen', slug: 'developers/extending' },
						{ label: 'Contributing', slug: 'developers/contributing' },
					],
				},
			],
			customCss: [
				'./src/styles/custom.css',
			],
		}),
	],
});
