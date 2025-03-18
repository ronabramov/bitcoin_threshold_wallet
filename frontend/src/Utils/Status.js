export const numberToStatus = {
     '-2':'Aborted',
     '-1':'Declined',
     '0':'Pending to your approval',
     '1':'Pending other\'s approval',
     '2':'Stage One',
     '3':'Stage Two',
     '4':'Stage Three',
     '5':'Stage Four',
     '6':'Completed',
     '7':'Processing'
}

export const statusColors = {
     '-2': '#dc3545', // Red for aborted
    '-1': '#dc3545', // Red for declined
    '0': '#ffffff', // white  for pending
    '1': '#ffa726', // Orange for pending
    '2': '#3f51b5', // Indigo for stage one
    '3': '#2196f3', // Blue for stage two
    '4': '#9c27b0', // Purple for stage three
    '5': '#009688', // Teal for stage four
    '6': '#4caf50', // Green for completed
    '7': '#009688' // Teal for processing
}