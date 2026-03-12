import http from './http'
import type {
  DeleteFolderResponse,
  DeleteImageResponse,
  ImageFolderDetailResponse,
  ImageFolderListResponse,
  UploadImagesResponse
} from '@/features/image-library/types'

export const uploadImages = async (
  folderSlug: string,
  files: File[],
  overwrite = false
) => {
  const formData = new FormData()
  formData.append('folder_slug', folderSlug)
  formData.append('overwrite', String(overwrite))
  for (const file of files) {
    formData.append('images', file)
  }

  const { data } = await http.post<UploadImagesResponse>('/images', formData)
  return data
}

export const fetchImageFolders = async () => {
  const { data } = await http.get<ImageFolderListResponse>('/image-folders')
  return data.folders
}

export const fetchImageFolder = async (folderSlug: string) => {
  const { data } = await http.get<ImageFolderDetailResponse>(`/image-folders/${encodeURIComponent(folderSlug)}`)
  return data
}

export const deleteImage = async (folderSlug: string, fileName: string) => {
  const { data } = await http.delete<DeleteImageResponse>(
    `/image-folders/${encodeURIComponent(folderSlug)}/images/${encodeURIComponent(fileName)}`
  )
  return data
}

export const deleteImageFolder = async (folderSlug: string) => {
  const { data } = await http.delete<DeleteFolderResponse>(`/image-folders/${encodeURIComponent(folderSlug)}`)
  return data
}
