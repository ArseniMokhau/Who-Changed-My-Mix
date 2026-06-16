import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn } from 'typeorm';

@Entity('audio_metadata')
export class AudioMetadata {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  originalFileName: string;

  @Column()
  storagePath: string; 

  @Column({ default: 'PENDING' })
  status: string;

  @Column({ nullable: true })
  blockchainHash: string;

  @CreateDateColumn()
  createdAt: Date;

  @Column({ type: 'float', nullable: true })
  manipulationScore: number;

  @Column({ type: 'boolean', nullable: true })
  isManipulated: boolean;
}