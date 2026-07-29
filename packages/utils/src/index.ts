// Utility Functions Skeleton
export const slugify = (text: string): string => {
  return text.toLowerCase().replace(/[^\w ]+/g, '').replace(/ +/g, '-');
};
