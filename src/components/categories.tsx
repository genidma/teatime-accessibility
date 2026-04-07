import type { ReactNode } from 'react';
import { Brain, Sparkles, Heart, BookOpen, Zap, Timer, Activity, Coffee, Dumbbell, WalkieTalkie } from 'lucide-react';

export type CategoryStyle = {
  id: string;
  name: string;
  icon: ReactNode;
  color: string;
  bgColor: string;
  label: string;
  borderColor?: string;
};

export const CATEGORY_STYLES: Record<string, CategoryStyle> = {
  'deep-work': {
    id: 'deep-work',
    name: 'Deep Work',
    icon: <Brain className="w-6 h-6" />,
    color: 'text-[#0051ae]',
    bgColor: 'bg-[#0969da]',
    label: 'DW',
  },
  'meditation': {
    id: 'meditation',
    name: 'Meditation',
    icon: <Sparkles className="w-6 h-6" />,
    color: 'text-[#0a6148]',
    bgColor: 'bg-[#2e7a5f]',
    label: 'M',
  },
  'gratitude': {
    id: 'gratitude',
    name: 'Gratitude',
    icon: <Heart className="w-6 h-6" />,
    color: 'text-[#9b4500]',
    bgColor: 'bg-[#fd8a42]',
    label: 'G',
  },
  'break': {
    id: 'break',
    name: 'Break',
    icon: <Coffee className="w-6 h-6" />,
    color: 'text-[#727785]',
    bgColor: 'bg-[#e4e8f0]',
    label: 'BR',
  },
  'exercise': {
    id: 'exercise',
    name: 'Exercise',
    icon: <Dumbbell className="w-6 h-6" />,
    color: 'text-[#ba1a1a]',
    bgColor: 'bg-[#ffdad6]',
    label: 'EX',
  },
  'walk': {
    id: 'walk',
    name: 'Walk',
    icon: <WalkieTalkie className="w-6 h-6" />,
    color: 'text-[#424753]',
    bgColor: 'bg-[#dee3eb]',
    label: 'WK',
  },
};

export const DEFAULT_CATEGORIES: CategoryStyle[] = [
  CATEGORY_STYLES['deep-work'],
  CATEGORY_STYLES['meditation'],
  CATEGORY_STYLES['gratitude'],
];

export function getCategoryStyle(categoryId: string): CategoryStyle {
  return CATEGORY_STYLES[categoryId] || CATEGORY_STYLES['deep-work'];
}

export function getAllCategories(): CategoryStyle[] {
  return Object.values(CATEGORY_STYLES);
}

export function getCategoryIcon(categoryId: string): ReactNode {
  return getCategoryStyle(categoryId).icon;
}

export function getCategoryColor(categoryId: string): string {
  return getCategoryStyle(categoryId).color;
}

export function getCategoryBgColor(categoryId: string): string {
  return getCategoryStyle(categoryId).bgColor;
}

export function getCategoryLabel(categoryId: string): string {
  return getCategoryStyle(categoryId).label;
}
