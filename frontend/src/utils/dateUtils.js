export const formatDate = (date) => {
  if (!date) return '';
  const d = new Date(date);
  return `${d.getDate()?.toString().padStart(2, '0')}${(d.getMonth() + 1)?.toString().padStart(2, '0')}${d.getFullYear()}`;
};

export const parseDate = (dateString) => {
  if (!dateString) return null;
  const day = parseInt(dateString.substring(0, 2), 10);
  const month = parseInt(dateString.substring(2, 4), 10) - 1;
  const year = parseInt(dateString.substring(4, 8), 10);
  return new Date(year, month, day);
};

export function formatDDMMYYYY(input) {
  if (input.length !== 8) return "Invalid Date";

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  let day = input.slice(0, 2);
  let mIdx = Number(input.slice(2, 4));
  let month = months[mIdx - 1];
  let year = input.slice(4, 8);

  return `${day} ${month} ${year}`;
}