import { defineCollection, z } from 'astro:content';

const services = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    intro: z.string(),
    deliverables: z.array(z.string()),
    featured_portfolio_slugs: z.array(z.string()).optional(),
  }),
});

export const collections = { services };
