import { NextRequest, NextResponse } from 'next/server';
import { writeFile, mkdir } from 'fs/promises';
import path from 'path';
import { existsSync } from 'fs';

export async function POST(request) {
  try {
    const formData = await request.formData();
    const file = formData.get('file');
    const courseName = formData.get('courseName');
    const courseType = formData.get('courseType');

    if (!file || !courseName || !courseType) {
      return NextResponse.json(
        { error: 'Arquivo, nome do curso e tipo são obrigatórios' },
        { status: 400 }
      );
    }

    // Verificar se é um arquivo PDF
    if (file.type !== 'application/pdf') {
      return NextResponse.json(
        { error: 'Apenas arquivos PDF são aceitos' },
        { status: 400 }
      );
    }

    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    // Criar diretório para matrizes curriculares se não existir
    const uploadsDir = path.join(process.cwd(), 'public', 'uploads', 'curricula');
    if (!existsSync(uploadsDir)) {
      await mkdir(uploadsDir, { recursive: true });
    }

    // Gerar nome único para o arquivo
    const timestamp = Date.now();
    const sanitizedCourseName = courseName
      .toLowerCase()
      .replace(/[^a-z0-9\s]/gi, '')
      .replace(/\s+/g, '_')
      .substring(0, 50);
    
    const fileName = `${sanitizedCourseName}_${timestamp}.pdf`;
    const filePath = path.join(uploadsDir, fileName);

    // Salvar o arquivo
    await writeFile(filePath, buffer);

    // Registrar informações da matriz curricular no arquivo JSON
    const curriculaInfoPath = path.join(process.cwd(), 'data', 'curricula.json');
    
    // Criar diretório data se não existir
    const dataDir = path.join(process.cwd(), 'data');
    if (!existsSync(dataDir)) {
      await mkdir(dataDir, { recursive: true });
    }

    let curricula = [];
    try {
      if (existsSync(curriculaInfoPath)) {
        const curriculaData = await require('fs/promises').readFile(curriculaInfoPath, 'utf-8');
        curricula = JSON.parse(curriculaData);
      }
    } catch (error) {
      console.log('Criando novo arquivo de matrizes curriculares');
    }

    // Adicionar nova matriz curricular
    const newCurriculum = {
      id: timestamp,
      courseName,
      courseType,
      fileName,
      filePath: `/uploads/curricula/${fileName}`,
      uploadDate: new Date().toISOString(),
      fileSize: buffer.length
    };

    curricula.push(newCurriculum);

    // Salvar as informações atualizadas
    await writeFile(curriculaInfoPath, JSON.stringify(curricula, null, 2));

    return NextResponse.json({
      message: 'Matriz curricular enviada com sucesso',
      curriculum: newCurriculum
    });

  } catch (error) {
    console.error('Erro no upload:', error);
    return NextResponse.json(
      { error: 'Erro interno do servidor' },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    const curriculaInfoPath = path.join(process.cwd(), 'data', 'curricula.json');
    
    if (!existsSync(curriculaInfoPath)) {
      return NextResponse.json({ curricula: [] });
    }

    const curriculaData = await require('fs/promises').readFile(curriculaInfoPath, 'utf-8');
    const curricula = JSON.parse(curriculaData);

    return NextResponse.json({ curricula });
  } catch (error) {
    console.error('Erro ao buscar matrizes curriculares:', error);
    return NextResponse.json(
      { error: 'Erro ao buscar matrizes curriculares' },
      { status: 500 }
    );
  }
}

export async function DELETE(request) {
  try {
    const { id } = await request.json();
    
    if (!id) {
      return NextResponse.json(
        { error: 'ID é obrigatório' },
        { status: 400 }
      );
    }

    const curriculaInfoPath = path.join(process.cwd(), 'data', 'curricula.json');
    
    if (!existsSync(curriculaInfoPath)) {
      return NextResponse.json(
        { error: 'Matriz curricular não encontrada' },
        { status: 404 }
      );
    }

    const curriculaData = await require('fs/promises').readFile(curriculaInfoPath, 'utf-8');
    let curricula = JSON.parse(curriculaData);

    const curriculumIndex = curricula.findIndex(c => c.id === id);
    
    if (curriculumIndex === -1) {
      return NextResponse.json(
        { error: 'Matriz curricular não encontrada' },
        { status: 404 }
      );
    }

    const curriculum = curricula[curriculumIndex];

    // Remover arquivo físico
    const fullFilePath = path.join(process.cwd(), 'public', 'uploads', 'curricula', curriculum.fileName);
    try {
      await require('fs/promises').unlink(fullFilePath);
    } catch (error) {
      console.log('Arquivo já foi removido ou não existe:', error.message);
    }

    // Remover do array
    curricula.splice(curriculumIndex, 1);

    // Salvar as informações atualizadas
    await writeFile(curriculaInfoPath, JSON.stringify(curricula, null, 2));

    return NextResponse.json({
      message: 'Matriz curricular removida com sucesso'
    });

  } catch (error) {
    console.error('Erro ao remover matriz curricular:', error);
    return NextResponse.json(
      { error: 'Erro interno do servidor' },
      { status: 500 }
    );
  }
}
