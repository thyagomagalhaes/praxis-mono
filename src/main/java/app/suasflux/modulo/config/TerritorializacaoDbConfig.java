package app.suasflux.modulo.config;


import java.util.Objects;

import javax.sql.DataSource;

import org.flywaydb.core.Flyway;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.jdbc.autoconfigure.DataSourceProperties;
import org.springframework.boot.jpa.EntityManagerFactoryBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.DependsOn;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;

@Configuration
@EnableTransactionManagement
@EnableJpaRepositories(
        basePackages = "app.suasflux.modulo.territorializacao",
        entityManagerFactoryRef = "territorializacaoEntityManagerFactory",
        transactionManagerRef = "territorializacaoTransactionManager"
)
public class TerritorializacaoDbConfig {
	
	
    @Bean
    @ConfigurationProperties("app.datasource.territorializacao")
    public DataSourceProperties federacaoDataSourceProperties() {
        return new DataSourceProperties();
    }
	
	
    @Bean
    public DataSource territorioDataSource(
            @Qualifier("territorializacaoDataSourceProperties") DataSourceProperties properties) {
        return properties.initializeDataSourceBuilder().build();
    }
	
	
    @Bean
    public Flyway territorioFlyway(
            @Qualifier("territorioDataSource") DataSource dataSource) {
        return Flyway.configure()
                .dataSource(dataSource)
                .locations(
                    "classpath:db/setupschema/territorio",
                    "classpath:db/migration/territorio",
                    "classpath:db/legacydata/territorio"
                )
                .baselineOnMigrate(true)  // Útil para DBs existentes
                .load();
    }
	
	
    @Bean
    @DependsOn("territorioFlyway")  // Garante ordem sem injeção fantasma
    public LocalContainerEntityManagerFactoryBean territorioEntityManagerFactory(
            EntityManagerFactoryBuilder builder,
            @Qualifier("territorioDataSource") DataSource dataSource) {
        
        return builder
                .dataSource(dataSource)
                .packages("app.suasflux.modulo.territorializacao")
                .persistenceUnit("territorio")
                .build();
    }
	

    @Bean
    public PlatformTransactionManager territorioTransactionManager(
            @Qualifier("territorioEntityManagerFactory") 
            LocalContainerEntityManagerFactoryBean entityManagerFactory) {
        
        return new JpaTransactionManager(
            Objects.requireNonNull(entityManagerFactory.getObject(), 
                "EntityManagerFactory não inicializada")
        );
    }
}
